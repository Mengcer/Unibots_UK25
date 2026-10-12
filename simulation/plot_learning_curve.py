import os
import csv
import math

def analyze_log(csv_path="models/training_log.csv", html_out="models/learning_curve_dashboard.html"):
    if not os.path.exists(csv_path):
        print(f"Log file not found: {csv_path}")
        return

    timesteps = []
    rewards = []
    fps_list = []
    kl_list = []

    with open(csv_path, mode="r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                t = int(row["timestep"])
                r = float(row["mean_episode_reward"])
                fps = int(row["fps"])
                kl = float(row.get("approx_kl", 0.0))
                timesteps.append(t)
                rewards.append(r)
                fps_list.append(fps)
                kl_list.append(kl)
            except (ValueError, KeyError):
                continue

    if not timesteps:
        print("No valid data points found in training log.")
        return

    total_steps = timesteps[-1]
    avg_fps = sum(fps_list) / len(fps_list) if fps_list else 0

    # Moving average smoothing (window = 20)
    window = min(20, len(rewards))
    moving_avg = []
    for i in range(len(rewards)):
        start = max(0, i - window + 1)
        sub = rewards[start:i + 1]
        moving_avg.append(sum(sub) / len(sub))

    # Plateau Detection
    recent_window = min(50, len(rewards))
    if recent_window >= 10:
        recent_rewards = moving_avg[-recent_window:]
        recent_delta = recent_rewards[-1] - recent_rewards[0]
        step_delta = timesteps[-1] - timesteps[-recent_window]
        rate_of_improvement = (recent_delta / (step_delta / 1_000_000)) if step_delta > 0 else 0.0
    else:
        recent_delta = 0.0
        rate_of_improvement = 0.0

    current_perf = moving_avg[-1]
    max_perf = max(rewards)

    # Determine plateau diagnostic
    if abs(rate_of_improvement) < 0.25 and total_steps > 500_000:
        if current_perf < 10.0:
            status = "SUBOPTIMAL PLATEAU DETECTED"
            diagnosis = "Agent trapped in local minimum. Collecting 1-2 balls but exploration failed on 30s docking."
            action = "RESCALE METHOD: Inject Behavior Cloning (APF pre-training) or enable curriculum docking resets."
        elif current_perf < 30.0:
            status = "MODERATE PLATEAU"
            diagnosis = "Agent collecting moderately, but collision penalties or high learning rate limit docking."
            action = "RESCALE METHOD: Reduce learning rate to 5e-5 with Cosine Annealing, or tune motor smoothness reward."
        else:
            status = "CHAMPION PLATEAU (CONVERGED)"
            diagnosis = "Policy has achieved robust high-scoring collection and docking."
            action = "READY FOR HARDWARE: Distill to C++ decision tree (esp32_policy_tree.hpp) or run multi-agent tournament."
    else:
        status = "ACTIVE LEARNING"
        diagnosis = f"Policy is improving at {rate_of_improvement:+.2f} reward points per million timesteps."
        action = "CONTINUE TRAINING: Progressing along upward gradient."

    print("=" * 68)
    print("UNIBOTS PPO TRAINING & LEARNING CURVE ANALYSIS")
    print(f"Total Steps Recorded : {total_steps:,}")
    print(f"Average Throughput   : {avg_fps:.0f} FPS")
    print(f"Current Mean Reward  : {current_perf:.2f} (Peak: {max_perf:.2f})")
    print(f"Rate of Improvement  : {rate_of_improvement:+.3f} pts / 1M steps")
    print(f"Training Status      : {status}")
    print(f"Diagnostic           : {diagnosis}")
    print(f"Recommended Action   : {action}")
    print("=" * 68)

    # Milestones breakdown
    print("\n--- Training Milestones (every ~1M steps) ---")
    print(f"{'Step':<14} | {'Mean Reward':<12} | {'Smoothed':<10} | {'Approx KL'}")
    print("-" * 55)
    last_p = 0
    for i, (t, r, sm, kl) in enumerate(zip(timesteps, rewards, moving_avg, kl_list)):
        if t - last_p >= 950_000 or i == len(timesteps) - 1:
            print(f"{t:<14,} | {r:<12.2f} | {sm:<10.2f} | {kl:<.6f}")
            last_p = t

    # Generate interactive HTML dashboard
    generate_html_dashboard(timesteps, rewards, moving_avg, fps_list, kl_list, status, diagnosis, action, html_out)
    print(f"\n-> Interactive Learning Curve Dashboard saved to: {html_out}")

def generate_html_dashboard(timesteps, rewards, moving_avg, fps_list, kl_list, status, diagnosis, action, out_path):
    # Downsample points for lightweight web rendering
    step_skip = max(1, len(timesteps) // 150)
    sampled_t = timesteps[::step_skip]
    sampled_r = rewards[::step_skip]
    sampled_sm = moving_avg[::step_skip]

    labels = [f"{t/1_000_000:.1f}M" for t in sampled_t]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Unibots RL Training & Plateau Dashboard</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      padding: 24px;
      margin: 0;
    }}
    .card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }}
    .status-badge {{
      display: inline-block;
      padding: 6px 14px;
      border-radius: 9999px;
      font-weight: 700;
      font-size: 14px;
      background: {'#16a34a' if 'CHAMPION' in status or 'ACTIVE' in status else '#f59e0b'};
      color: #ffffff;
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-top: 16px;
    }}
    .metric-box {{
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 14px;
    }}
    .metric-title {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; }}
    .metric-value {{ font-size: 24px; font-weight: 700; color: #38bdf8; margin-top: 4px; }}
    svg {{ width: 100%; height: 320px; }}
    .chart-line {{ fill: none; stroke-width: 2.5; }}
  </style>
</head>
<body>
  <div class="card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h2 style="margin:0; color:#f8fafc;">Unibots RL Multi-Agent Training Dashboard</h2>
      <span class="status-badge">{status}</span>
    </div>
    <div class="metric-grid">
      <div class="metric-box">
        <div class="metric-title">Total Timesteps</div>
        <div class="metric-value">{timesteps[-1]:,}</div>
      </div>
      <div class="metric-box">
        <div class="metric-title">Peak Mean Reward</div>
        <div class="metric-value">{max(rewards):.2f}</div>
      </div>
      <div class="metric-box">
        <div class="metric-title">Latest Reward</div>
        <div class="metric-value">{moving_avg[-1]:.2f}</div>
      </div>
      <div class="metric-box">
        <div class="metric-title">Training FPS</div>
        <div class="metric-value">{sum(fps_list)/len(fps_list):.0f}</div>
      </div>
    </div>
  </div>

  <div class="card">
    <h3 style="margin-top:0; color:#38bdf8;">Diagnostic & Rescaling Recommendation</h3>
    <p><strong>Diagnosis:</strong> {diagnosis}</p>
    <p><strong>Recommended Strategy:</strong> {action}</p>
  </div>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    analyze_log()
