import numpy as np
from stable_baselines3 import PPO
from simulation.core import ArenaCore
from simulation.planner import NavigationPlanner
from simulation.sensors import Sensors

def run_tournament(match_duration_steps=5400, num_matches=5):
    """
    Runs three tournament tests:
    1. APF Only: All 4 robots running Classical APF Planner
    2. RL Only: All 4 robots running RL Neural Policy (4M checkpoint)
    3. Head-to-Head: 2 APF robots vs 2 RL robots in the same arena!
    """
    model_path = "models/unibots_ppo_v1.zip"
    model = PPO.load(model_path, device="cpu")

    def run_match(controller_types):
        # controller_types: list of 4 strings: 'APF' or 'RL'
        core = ArenaCore()
        sensors = Sensors(core)
        planners = [NavigationPlanner(core, i, sensors=sensors) for i in range(4)]

        for step in range(match_duration_steps):
            for i, ctype in enumerate(controller_types):
                r = core.robots[i]
                if ctype == 'APF':
                    vx, vy, omega = planners[i].compute_cmd()
                else:
                    obs = sensors.get_observation(i)
                    action, _ = model.predict(obs, deterministic=True)
                    vx = float(action[0]) * 500.0
                    vy = float(action[1]) * 300.0
                    omega = float(action[2]) * 3.14159
                r.vx = vx
                r.vy = vy
                r.omega = omega
            core.step()

        scores = [core.compute_game_points(r) for r in core.robots]
        held = [r.total_held_elements for r in core.robots]
        scored = [r.scored_atoms for r in core.robots]
        penalties = [r.collision_penalty_count for r in core.robots]
        return scores, held, scored, penalties

    print("=" * 70)
    print("UNIBOTS HEAD-TO-HEAD CONTROLLER BENCHMARK")
    print(f"Match Duration: {match_duration_steps/30:.0f} seconds (Full 180s Match)")
    print(f"Number of Matches per Test: {num_matches}")
    print("=" * 70)

    # 1. All Classical APF
    apf_scores, apf_penalties, apf_held = [], [], []
    for _ in range(num_matches):
        s, h, sc, p = run_match(['APF', 'APF', 'APF', 'APF'])
        apf_scores.extend(s)
        apf_penalties.extend(p)
        apf_held.extend(h)

    # 2. All RL Neural Policy
    rl_scores, rl_penalties, rl_held = [], [], []
    for _ in range(num_matches):
        s, h, sc, p = run_match(['RL', 'RL', 'RL', 'RL'])
        rl_scores.extend(s)
        rl_penalties.extend(p)
        rl_held.extend(h)

    # 3. Head-to-Head: 2 APF vs 2 RL
    h2h_apf_scores, h2h_rl_scores = [], []
    h2h_apf_pens, h2h_rl_pens = [], []
    for _ in range(num_matches):
        s, h, sc, p = run_match(['APF', 'APF', 'RL', 'RL'])
        h2h_apf_scores.extend([s[0], s[1]])
        h2h_apf_pens.extend([p[0], p[1]])
        h2h_rl_scores.extend([s[2], s[3]])
        h2h_rl_pens.extend([p[2], p[3]])

    print(f"\n--- TEST 1: ISOLATED MODES (All 4 robots running same controller) ---")
    print(f"Classical APF Planner  : Avg Score = {np.mean(apf_scores):.1f} pts | Avg Penalties = {np.mean(apf_penalties):.1f}")
    print(f"RL Neural Policy (PPO) : Avg Score = {np.mean(rl_scores):.1f} pts | Avg Penalties = {np.mean(rl_penalties):.1f}")

    print(f"\n--- TEST 2: HEAD-TO-HEAD IN SAME MATCH (2 APF vs 2 RL Robots) ---")
    print(f"Classical APF Robots   : Avg Score = {np.mean(h2h_apf_scores):.1f} pts | Avg Penalties = {np.mean(h2h_apf_pens):.1f}")
    print(f"RL Neural Robots       : Avg Score = {np.mean(h2h_rl_scores):.1f} pts | Avg Penalties = {np.mean(h2h_rl_pens):.1f}")
    print("=" * 70)

if __name__ == "__main__":
    run_tournament(match_duration_steps=5400, num_matches=3)
