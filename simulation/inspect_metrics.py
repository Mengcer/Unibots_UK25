import os
import math
import numpy as np
from stable_baselines3 import PPO
from simulation.core import ArenaCore
from simulation.sensors import Sensors
from simulation.planner import NavigationPlanner

def run_detailed_telemetry(controller_type="BC", num_matches=2, steps_per_match=5400):
    """
    Simulates full 180s matches under realistic DC motor physics and collects
    comprehensive game, motor, and electrical risk metrics.
    """
    model = None
    if controller_type in ["BC", "BC_PPO", "RL_24M"]:
        if controller_type == "BC":
            path = "models/unibots_bc_pretrained.zip"
        elif controller_type == "BC_PPO":
            path = "models/unibots_bc_ppo.zip"
        else:
            path = "models/checkpoints/unibots_ppo_24000000_steps.zip"
        if not os.path.exists(path):
            path = "models/unibots_ppo_v1.zip"
        model = PPO.load(path, device="cpu")

    match_stats = []

    for m in range(num_matches):
        core = ArenaCore()
        sensors = Sensors(core)
        planners = [NavigationPlanner(core, i, sensors=sensors) for i in range(4)]

        # Telemetry accumulators
        speed_samples = []
        cmd_speed_samples = []
        deadband_steps = 0
        jerk_samples = []
        penalty_freeze_steps = 0
        docking_steps = 0

        for step in range(steps_per_match):
            for i in range(4):
                r = core.robots[i]
                if controller_type == "APF":
                    vx, vy, omega = planners[i].compute_cmd()
                else:
                    obs = sensors.get_observation(i)
                    action, _ = model.predict(obs, deterministic=True)
                    vx = float(action[0]) * 500.0
                    vy = float(action[1]) * 300.0
                    omega = float(action[2]) * math.pi

                r.vx = vx
                r.vy = vy
                r.omega = omega

                cmd_spd = math.hypot(vx, vy)
                act_spd = math.hypot(r.actual_vx, r.actual_vy)
                cmd_speed_samples.append(cmd_spd)
                speed_samples.append(act_spd)
                jerk_samples.append(r.last_jerk)

                if act_spd < r.deadband_vel:
                    deadband_steps += 1
                if r.is_penalized:
                    penalty_freeze_steps += 1
                if r.is_depositing:
                    docking_steps += 1

            core.step()

        # Compute match totals
        total_pts = [core.compute_game_points(r) for r in core.robots]
        total_held = [r.total_held_elements for r in core.robots]
        total_scored = [r.scored_atoms for r in core.robots]
        total_penalties = [r.collision_penalty_count for r in core.robots]

        match_stats.append({
            "avg_points": np.mean(total_pts),
            "max_points": np.max(total_pts),
            "total_scored": np.sum(total_scored),
            "total_held": np.sum(total_held),
            "avg_penalties": np.mean(total_penalties),
            "avg_speed": np.mean(speed_samples),
            "avg_cmd_speed": np.mean(cmd_speed_samples),
            "deadband_pct": (deadband_steps / (steps_per_match * 4)) * 100.0,
            "max_jerk": np.max(jerk_samples),
            "avg_jerk": np.mean(jerk_samples),
            "freeze_time_pct": (penalty_freeze_steps / (steps_per_match * 4)) * 100.0,
            "docking_time_pct": (docking_steps / (steps_per_match * 4)) * 100.0,
        })

    # Aggregate across matches
    summary = {k: np.mean([ms[k] for ms in match_stats]) for k in match_stats[0].keys()}
    return summary

def main():
    print("=" * 75)
    print("UNIBOTS COMPREHENSIVE TELEMETRY & CONTROLLER METRICS INSPECTION")
    print("Match Conditions: 180s duration at 30Hz (5,400 steps) with Toy DC Motor Dynamics")
    print("=" * 75)

    controllers = ["APF", "BC"]
    if os.path.exists("models/unibots_bc_ppo.zip"):
        controllers.append("BC_PPO")
    if os.path.exists("models/checkpoints/unibots_ppo_24000000_steps.zip"):
        controllers.append("RL_24M")

    results = {}
    for c in controllers:
        name_map = {
            "APF": "Classical APF Planner (Expert)",
            "BC": "Behavior Cloned Policy (Pre-trained Baseline)",
            "BC_PPO": "Fine-Tuned BC+RL Champion Policy",
            "RL_24M": "Pure RL (Scratch Checkpoint 24M Steps)"
        }
        print(f"Evaluating {name_map[c]} across 2 matches...")
        results[c] = run_detailed_telemetry(controller_type=c, num_matches=2)

    print("\n" + "=" * 90)
    print(f"{'METRIC':<36} | {'APF EXPERT':<11} | {'BC BASELINE':<11} | {'BC+RL CHAMP':<11} | {'PURE RL 24M'}")
    print("-" * 90)

    has_rl = "RL_24M" in results
    has_bcppo = "BC_PPO" in results
    def fmt(val): return f"{val:.1f}"

    rows = [
        ("Avg Match Points / Robot", "avg_points"),
        ("Max Single Robot Points", "max_points"),
        ("Total Atoms Scored into Net", "total_scored"),
        ("Total Atoms Remaining in C-Cup", "total_held"),
        ("Avg Collision Penalties (10s lock)", "avg_penalties"),
        ("Time Frozen in Penalty (%)", "freeze_time_pct"),
        ("Time Docked in Deposit (%)", "docking_time_pct"),
        ("Avg Physical Speed (mm/s)", "avg_speed"),
        ("Avg Commanded Speed (mm/s)", "avg_cmd_speed"),
        ("Time in Motor Deadband (%)", "deadband_pct"),
        ("Mean Acceleration Jerk (mm/s²)", "avg_jerk"),
        ("Max Acceleration Jerk (mm/s²)", "max_jerk"),
    ]

    for label, key in rows:
        apf_v = results["APF"][key]
        bc_v = results["BC"][key]
        bcppo_v = results["BC_PPO"][key] if has_bcppo else 0.0
        rl_str = fmt(results["RL_24M"][key]) if has_rl else "N/A"
        print(f"{label:<36} | {apf_v:<11.1f} | {bc_v:<11.1f} | {bcppo_v:<11.1f} | {rl_str}")

    print("=" * 90)

if __name__ == "__main__":
    main()
