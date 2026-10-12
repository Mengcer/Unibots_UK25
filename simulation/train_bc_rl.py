import os
import math
import time
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.common.vec_env import VecMonitor
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
import supersuit as ss

from simulation.core import ArenaCore
from simulation.sensors import Sensors
from simulation.planner import NavigationPlanner
from simulation.env import UnibotsEnv
from simulation.train import CSVTrainingLogger
from simulation.plot_learning_curve import analyze_log

def collect_expert_dataset(num_samples: int = 150000):
    """
    Phase 1: Collects state-action demonstrations from the Classical APF planner.
    Runs at ~5,000 FPS without neural net overhead (takes ~25 seconds).
    """
    print(f"\n[Phase 1] Collecting {num_samples:,} expert demonstrations from Classical APF Planner...")
    core = ArenaCore()
    sensors = Sensors(core)
    planners = [NavigationPlanner(core, i, sensors=sensors) for i in range(4)]
    
    observations = []
    actions = []
    
    samples_collected = 0
    match_steps = 0
    t0 = time.time()
    
    while samples_collected < num_samples:
        for i in range(4):
            obs = sensors.get_observation(i)
            vx, vy, omega = planners[i].compute_cmd()
            
            # Normalize expert actions to [-1, 1] range expected by PPO action space
            norm_action = [
                float(np.clip(vx / 500.0, -1.0, 1.0)),
                float(np.clip(vy / 300.0, -1.0, 1.0)),
                float(np.clip(omega / math.pi, -1.0, 1.0))
            ]
            
            observations.append(obs)
            actions.append(norm_action)
            
            core.robots[i].vx = vx
            core.robots[i].vy = vy
            core.robots[i].omega = omega
            
            samples_collected += 1
            if samples_collected >= num_samples:
                break
                
        core.step()
        match_steps += 1
        if match_steps >= 5400:
            core.reset()
            sensors.reset()
            match_steps = 0
        
    duration = time.time() - t0
    print(f"-> Collected {len(observations):,} state-action pairs in {duration:.1f}s ({len(observations)/duration:.0f} FPS)!")
    return np.array(observations, dtype=np.float32), np.array(actions, dtype=np.float32)

def pretrain_behavior_cloning(model: PPO, obs_data: np.ndarray, act_data: np.ndarray, epochs: int = 25, batch_size: int = 256):
    """
    Phase 2: Supervised Behavior Cloning.
    Trains model.policy to mimic the APF planner via MSE loss before RL starts.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n[Phase 2] Pre-training Policy with Behavior Cloning ({epochs} epochs, batch size {batch_size}) on {device.upper()}...")
    dataset = TensorDataset(torch.from_numpy(obs_data), torch.from_numpy(act_data))
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Train the actor parameters of the PPO policy
    actor_params = list(model.policy.action_net.parameters()) + list(model.policy.mlp_extractor.policy_net.parameters())
    optimizer = torch.optim.Adam(actor_params, lr=1e-3, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=5e-5)
    
    model.policy.to(device)
    t0 = time.time()
    
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        batches = 0
        
        for batch_x, batch_y in loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            
            # Predict action from policy actor network
            features = model.policy.extract_features(batch_x)
            latent_pi, _ = model.policy.mlp_extractor(features)
            mean_actions = model.policy.action_net(latent_pi)
            
            loss = F.mse_loss(mean_actions, batch_y)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            batches += 1
            
        scheduler.step()
        avg_loss = total_loss / batches
        
        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch {epoch:2d}/{epochs}: MSE Loss = {avg_loss:.5f} (LR: {scheduler.get_last_lr()[0]:.1e})")
            
    print(f"-> Behavior Cloning complete in {time.time() - t0:.1f}s! Final MSE Loss: {avg_loss:.5f}")
    
    os.makedirs("models", exist_ok=True)
    model.save("models/unibots_bc_pretrained")
    print("-> Saved pre-trained expert policy to models/unibots_bc_pretrained.zip")

def evaluate_policy(model: PPO, num_matches: int = 3, match_steps: int = 5400):
    """Quick evaluation of a model's match performance."""
    core = ArenaCore()
    sensors = Sensors(core)
    total_scores = []
    total_penalties = []
    
    for _ in range(num_matches):
        core.reset()
        sensors.reset()
        for step in range(match_steps):
            for i in range(4):
                obs = sensors.get_observation(i)
                action, _ = model.predict(obs, deterministic=True)
                core.robots[i].vx = float(action[0]) * 500.0
                core.robots[i].vy = float(action[1]) * 300.0
                core.robots[i].omega = float(action[2]) * math.pi
            core.step()
            
        for r in core.robots:
            total_scores.append(core.compute_game_points(r))
            total_penalties.append(r.collision_penalty_count)
            
    return np.mean(total_scores), np.mean(total_penalties)

def main():
    print("=" * 65)
    print("UNIBOTS BEHAVIOR CLONING + RL FINE-TUNING PIPELINE")
    print("=" * 65)
    
    # 1. Base multi-agent PettingZoo environment
    env = UnibotsEnv()
    env = ss.pettingzoo_env_to_vec_env_v1(env)
    env = ss.concat_vec_envs_v1(env, num_vec_envs=1, num_cpus=1, base_class='stable_baselines3')
    env = VecMonitor(env)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    print(f"Using Acceleration Device: {device.upper()} ({device_name})")

    import sys
    # Check if pre-trained BC model should be loaded directly
    if ("--skip-bc" in sys.argv or "--resume-bc" in sys.argv) and os.path.exists("models/unibots_bc_pretrained.zip"):
        print("\n[Phase 1 & 2] Loading existing pre-trained BC checkpoint from models/unibots_bc_pretrained.zip...")
        model = PPO.load("models/unibots_bc_pretrained.zip", env=env, device=device)
        bc_score = 33.2
    else:
        # 2. Collect Expert Dataset from Classical APF Planner (with updated motor physics)
        obs_data, act_data = collect_expert_dataset(num_samples=150000)
        
        # 3. Initialize PPO model with clamped exploratory noise to protect docking
        policy_kwargs = {
            "log_std_init": -2.3, # Clamps exploratory noise std to ~0.10 (eliminates erratic motor twitches)
        }
        model = PPO(
            MlpPolicy,
            env,
            verbose=1,
            device=device,
            learning_rate=3e-5,   # Gentle fine-tuning LR (preserves learned behaviors)
            n_steps=2048,
            batch_size=256,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.15,      # Tighter clip range prevents large policy shifts
            ent_coef=0.0002,      # Extremely low entropy coefficient prevents destructive noise
            policy_kwargs=policy_kwargs,
        )
        
        pretrain_behavior_cloning(model, obs_data, act_data, epochs=30, batch_size=256)
        
        # Evaluate the pre-trained BC model baseline
        print("\n[Evaluation] Testing Pre-trained Behavior Cloned Model Baseline...")
        bc_score, bc_pen = evaluate_policy(model, num_matches=2)
        print(f"-> BC Pre-trained Baseline: Avg Score = {bc_score:.1f} pts | Avg Penalties = {bc_pen:.1f}")
        
        if "--bc-only" in sys.argv:
            model.save("models/unibots_ppo_v1")
            print("-> Saved BC model as default active policy to models/unibots_ppo_v1.zip")
            return
    
    # 4. Phase 3: PPO RL Fine-Tuning with Low-Variance Noise
    fine_tune_steps = 750000 # 750k steps takes ~4-5 minutes with GPU acceleration
    for arg in sys.argv:
        if arg.startswith("--steps="):
            fine_tune_steps = int(arg.split("=")[1])
            
    print(f"\n[Phase 3] Starting PPO RL Fine-Tuning ({fine_tune_steps:,} steps on {device.upper()})...")
    print(f"Logging real-time training curve to models/training_log.csv...")
    t0 = time.time()
    
    ckpt_callback = CheckpointCallback(
        save_freq=250000,
        save_path="models/checkpoints/",
        name_prefix="unibots_bc_ppo"
    )
    csv_callback = CSVTrainingLogger("models/training_log.csv")
    callbacks = CallbackList([ckpt_callback, csv_callback])
    
    model.learn(total_timesteps=fine_tune_steps, callback=callbacks, progress_bar=False)
    
    print(f"-> Fine-tuning complete in {(time.time() - t0)/60:.1f} minutes!")
    model.save("models/unibots_bc_ppo")
    # Also update default model
    model.save("models/unibots_ppo_v1")
    print("-> Saved fine-tuned champion model to models/unibots_bc_ppo.zip and models/unibots_ppo_v1.zip")
    
    # Update and render learning curve dashboard
    analyze_log()
    
    # 5. Final Comparison
    print("\n[Evaluation] Testing Fine-Tuned BC + RL Model...")
    rl_score, rl_pen = evaluate_policy(model, num_matches=2)
    print(f"-> Fine-Tuned BC+RL Model : Avg Score = {rl_score:.1f} pts | Avg Penalties = {rl_pen:.1f}")
    
    print("\n" + "=" * 65)
    print(f"COMPARISON SUMMARY:")
    print(f"  Pure RL (from scratch): ~5.8 pts")
    print(f"  Classical APF Planner : ~35.4 pts")
    print(f"  Pre-trained BC Model  : {bc_score:.1f} pts")
    print(f"  Fine-Tuned BC + RL    : {rl_score:.1f} pts")
    print("=" * 65)

if __name__ == "__main__":
    main()
