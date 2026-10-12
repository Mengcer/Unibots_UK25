import os
import pickle
import numpy as np
from simulation.core import ArenaCore
from simulation.sensors import Sensors
from simulation.controllers import (
    APFController,
    FlatRLController,
    HierarchicalHybridController,
    MacroRLController,
    DecisionTreeController
)

def create_controller(ctype: str, core: ArenaCore, robot_id: int, sensors: Sensors, tree=None):
    if ctype == "APF":
        return APFController(core, robot_id, sensors)
    elif ctype == "Flat_RL":
        return FlatRLController(core, robot_id, sensors)
    elif ctype == "HRL_Hybrid":
        return HierarchicalHybridController(core, robot_id, sensors)
    elif ctype == "Macro_RL":
        return MacroRLController(core, robot_id, sensors)
    elif ctype == "Tree_Policy":
        return DecisionTreeController(core, robot_id, sensors, tree=tree)
    else:
        raise ValueError(f"Unknown controller type: {ctype}")

def run_match(controller_types, tree=None, match_steps=5400):
    core = ArenaCore()
    sensors = Sensors(core)
    ctrls = [create_controller(ctype, core, i, sensors, tree=tree) for i, ctype in enumerate(controller_types)]
    
    for _ in range(match_steps):
        for i in range(4):
            vx, vy, omega = ctrls[i].compute_cmd()
            core.robots[i].vx = vx
            core.robots[i].vy = vy
            core.robots[i].omega = omega
        core.step()
        
    scores = [core.compute_game_points(r) for r in core.robots]
    penalties = [r.collision_penalty_count for r in core.robots]
    held = [r.total_held_elements for r in core.robots]
    return scores, penalties, held

def main():
    tree_path = "models/decision_tree_policy.pkl"
    tree = None
    if os.path.exists(tree_path):
        with open(tree_path, "rb") as f:
            tree = pickle.load(f)

    controllers = ["APF", "Flat_RL", "HRL_Hybrid", "Macro_RL", "Tree_Policy"]
    
    print("=" * 75)
    print("GRAND 5-WAY AUTONOMOUS CONTROLLER BENCHMARK")
    print("Models Tested:")
    print("  1. APF         : Classical Artificial Potential Fields")
    print("  2. Flat_RL     : End-to-End PPO Neural Policy")
    print("  3. HRL_Hybrid  : Option A (Decision Tree Macro + RL Agility Pilot)")
    print("  4. Macro_RL    : Option B (Macro-Strategic RL + APF Driver)")
    print("  5. Tree_Policy : Option C (Distilled Decision Tree, C++ Exportable)")
    print("=" * 75)

    num_matches = 2
    
    # -------------------------------------------------------------
    # 1. ISOLATED BENCHMARK (All 4 robots running the same controller)
    # -------------------------------------------------------------
    print("\n--- STAGE 1: ISOLATED BENCHMARK (All 4 robots run same controller) ---")
    isolated_results = {}
    for ctype in controllers:
        scores, pens = [], []
        for _ in range(num_matches):
            s, p, h = run_match([ctype] * 4, tree=tree)
            scores.extend(s)
            pens.extend(p)
        avg_score = float(np.mean(scores))
        avg_pen = float(np.mean(pens))
        isolated_results[ctype] = (avg_score, avg_pen)
        print(f"  {ctype:<12} : Avg Score = {avg_score:5.1f} pts | Avg Penalties = {avg_pen:4.1f}")

    # -------------------------------------------------------------
    # 2. HEAD-TO-HEAD 2 vs 2 TOURNAMENT MATCHUPS
    # -------------------------------------------------------------
    print("\n--- STAGE 2: HEAD-TO-HEAD 2 vs 2 TOURNAMENTS ---")
    matchups = [
        ("HRL_Hybrid", "APF"),
        ("HRL_Hybrid", "Flat_RL"),
        ("Macro_RL", "APF"),
        ("Tree_Policy", "APF"),
        ("Tree_Policy", "Flat_RL"),
    ]
    
    for team_a, team_b in matchups:
        a_scores, b_scores = [], []
        a_pens, b_pens = [], []
        for _ in range(num_matches):
            s, p, h = run_match([team_a, team_a, team_b, team_b], tree=tree)
            a_scores.extend([s[0], s[1]])
            b_scores.extend([s[2], s[3]])
            a_pens.extend([p[0], p[1]])
            b_pens.extend([p[2], p[3]])
        winner = team_a if np.mean(a_scores) >= np.mean(b_scores) else team_b
        print(f"  [Matchup] {team_a} (Team A) vs {team_b} (Team B):")
        print(f"    Team A ({team_a:11}): {np.mean(a_scores):4.1f} pts (Pens: {np.mean(a_pens):.1f})")
        print(f"    Team B ({team_b:11}): {np.mean(b_scores):4.1f} pts (Pens: {np.mean(b_pens):.1f})")
        print(f"    -> WINNER: {winner}\n")

    print("=" * 75)
    print("GRAND TOURNAMENT SUMMARY (RANKED BY ISOLATED PERFORMANCE):")
    sorted_ranks = sorted(isolated_results.items(), key=lambda x: x[1][0], reverse=True)
    for rank, (name, (score, pens)) in enumerate(sorted_ranks, 1):
        print(f"  #{rank}: {name:<12} | Avg Score: {score:4.1f} pts | Penalties: {pens:.1f}")
    print("=" * 75)

if __name__ == "__main__":
    main()
