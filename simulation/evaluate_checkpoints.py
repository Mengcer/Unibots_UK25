import os
import glob
from stable_baselines3 import PPO
from simulation.core import ArenaCore
from simulation.sensors import Sensors

def evaluate_checkpoint(model_path: str, num_steps: int = 1800):
    """Simulates a match (60s at 30Hz) and returns performance metrics."""
    core = ArenaCore()
    sensors = Sensors(core)
    model = PPO.load(model_path, device="cpu")

    for step in range(num_steps):
        for i, r in enumerate(core.robots):
            obs = sensors.get_observation(i)
            action, _ = model.predict(obs, deterministic=True)
            r.vx = float(action[0]) * 500.0
            r.vy = float(action[1]) * 300.0
            r.omega = float(action[2]) * 3.14159
        core.step()

    total_points = sum(core.compute_game_points(r) for r in core.robots)
    avg_points = total_points / len(core.robots)
    total_held = sum(r.total_held_elements for r in core.robots)
    total_scored = sum(r.scored_atoms for r in core.robots)
    total_penalties = sum(r.collision_penalty_count for r in core.robots)

    return {
        "avg_points": avg_points,
        "total_held": total_held,
        "total_scored": total_scored,
        "total_penalties": total_penalties
    }

def main():
    ckpts = sorted(glob.glob("models/checkpoints/unibots_ppo_*_steps.zip"), 
                   key=lambda p: int(os.path.basename(p).split('_')[2]))
    
    # Include final model
    models_to_test = ckpts + ["models/unibots_ppo_v1.zip"]
    
    print("=" * 65)
    print("UNIBOTS PPO CHECKPOINT BENCHMARK & EVALUATION")
    print(f"Testing {len(models_to_test)} checkpoints across standard matches...")
    print("=" * 65)
    print(f"{'Checkpoint':<32} | {'Avg Pts':<8} | {'Held':<6} | {'Scored':<7} | {'Penalties'}")
    print("-" * 65)

    best_ckpt = None
    best_score = -1

    for mpath in models_to_test:
        name = os.path.basename(mpath)
        metrics = evaluate_checkpoint(mpath)
        print(f"{name:<32} | {metrics['avg_points']:<8.1f} | {metrics['total_held']:<6} | {metrics['total_scored']:<7} | {metrics['total_penalties']}")
        
        if metrics['avg_points'] > best_score:
            best_score = metrics['avg_points']
            best_ckpt = name

    print("=" * 65)
    print(f"OPTIMAL CHECKPOINT: {best_ckpt} with {best_score:.1f} avg points!")
    print("=" * 65)

if __name__ == "__main__":
    main()
