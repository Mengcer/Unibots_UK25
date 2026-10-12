import os
import time
import csv
import torch
from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.common.callbacks import CheckpointCallback, BaseCallback, CallbackList
from stable_baselines3.common.vec_env import VecMonitor
import supersuit as ss
from simulation.env import UnibotsEnv

class CSVTrainingLogger(BaseCallback):
    """
    Logs learning progress metrics to a clean CSV file so the user can easily
    determine the exact optimal training length and plateau point in the morning.
    """
    def __init__(self, log_path: str, verbose: int = 0):
        super().__init__(verbose)
        self.log_path = log_path
        self.start_time = None
        self.file = None
        self.writer = None

    def _on_training_start(self):
        self.start_time = time.time()
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self.file = open(self.log_path, mode="w", newline="", buffering=1)
        self.writer = csv.writer(self.file)
        self.writer.writerow(["timestep", "elapsed_seconds", "fps", "mean_episode_reward", "approx_kl"])

    def _on_step(self) -> bool:
        return True

    def _on_rollout_end(self):
        elapsed = time.time() - self.start_time
        timesteps = self.num_timesteps
        fps = int(timesteps / elapsed) if elapsed > 0 else 0
        
        ep_rew_mean = self.logger.name_to_value.get("rollout/ep_rew_mean", 0.0)
        approx_kl = self.logger.name_to_value.get("train/approx_kl", 0.0)
        
        self.writer.writerow([timesteps, f"{elapsed:.1f}", fps, f"{ep_rew_mean:.2f}", f"{approx_kl:.6f}"])
        self.file.flush()

    def _on_training_end(self):
        if self.file:
            self.file.close()

def train(total_timesteps: int = 25000000):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    print(f"==================================================")
    print(f"Unibots PPO Multi-Agent Long Training")
    print(f"Training Device: {device.upper()} ({device_name})")
    print(f"Target Timesteps: {total_timesteps:,}")
    print(f"Checkpoints every: 500,000 steps in models/checkpoints/")
    print(f"Learning Curve Log: models/training_log.csv")
    print(f"==================================================")

    # Base multi-agent PettingZoo environment
    env = UnibotsEnv()
    
    # Vectorize the 4 robot agents to train simultaneously
    env = ss.pettingzoo_env_to_vec_env_v1(env)
    env = ss.concat_vec_envs_v1(env, num_vec_envs=1, num_cpus=1, base_class='stable_baselines3')
    env = VecMonitor(env) # Enables SB3 logger to record true rollout/ep_rew_mean curves!

    # Initialize PPO model with 32-dim spatial memory observation space
    model = PPO(
        MlpPolicy,
        env,
        verbose=1,
        device=device,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=256,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01, # Encourage exploration of ball clusters
    )

    os.makedirs("models/checkpoints", exist_ok=True)

    # 1. Checkpoint callback: saves every 500k timesteps
    checkpoint_callback = CheckpointCallback(
        save_freq=500000,
        save_path="models/checkpoints/",
        name_prefix="unibots_ppo",
        save_replay_buffer=False,
        save_vecnormalize=False
    )

    # 2. CSV training progress logger callback
    csv_callback = CSVTrainingLogger(log_path="models/training_log.csv")

    callbacks = CallbackList([checkpoint_callback, csv_callback])

    print("Starting Multi-Agent PPO training...")
    try:
        model.learn(total_timesteps=total_timesteps, callback=callbacks, progress_bar=False)
        model.save("models/unibots_ppo_v1")
        print("\nTraining complete! Final model saved to models/unibots_ppo_v1.zip")
    except KeyboardInterrupt:
        print("\nTraining interrupted by user. Saving current checkpoint...")
        model.save("models/unibots_ppo_interrupted")
        model.save("models/unibots_ppo_v1")
        print("Checkpoint saved to models/unibots_ppo_v1.zip and models/unibots_ppo_interrupted.zip")

if __name__ == "__main__":
    train()
