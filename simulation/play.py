import os
import pygame
import pickle
import numpy as np
from simulation.core import ArenaCore
from simulation.render import Visualizer
from simulation.sensors import Sensors
from simulation.controllers import (
    APFController,
    FlatRLController,
    HierarchicalHybridController,
    MacroRLController,
    DecisionTreeController
)

def create_ctrl(ctype: str, core: ArenaCore, robot_id: int, sensors: Sensors, tree=None):
    if ctype == "APF": return APFController(core, robot_id, sensors)
    elif ctype == "Flat_RL": return FlatRLController(core, robot_id, sensors)
    elif ctype == "HRL_Hybrid": return HierarchicalHybridController(core, robot_id, sensors)
    elif ctype == "Macro_RL": return MacroRLController(core, robot_id, sensors)
    elif ctype == "Tree_Policy": return DecisionTreeController(core, robot_id, sensors, tree=tree)
    else: return APFController(core, robot_id, sensors)

def main():
    core = ArenaCore()
    sensors = Sensors(core)
    vis = Visualizer(core)
    
    # Load Decision Tree if available
    tree_path = "models/decision_tree_policy.pkl"
    tree = None
    if os.path.exists(tree_path):
        with open(tree_path, "rb") as f:
            tree = pickle.load(f)

    # 7 Competitive Match Modes
    modes = [
        {"name": "2v2: HRL Hybrid (Yellow/Orange) vs APF (Purple/Green)", "controllers": ['HRL_Hybrid', 'HRL_Hybrid', 'APF', 'APF']},
        {"name": "2v2: APF (Yellow/Orange) vs Flat RL (Purple/Green)", "controllers": ['APF', 'APF', 'Flat_RL', 'Flat_RL']},
        {"name": "2v2: HRL Hybrid (Yellow/Orange) vs Tree Policy (Purple/Green)", "controllers": ['HRL_Hybrid', 'HRL_Hybrid', 'Tree_Policy', 'Tree_Policy']},
        {"name": "All 4 Robots: HRL Hybrid Champion (Option A)", "controllers": ['HRL_Hybrid', 'HRL_Hybrid', 'HRL_Hybrid', 'HRL_Hybrid']},
        {"name": "All 4 Robots: Classical APF Planner", "controllers": ['APF', 'APF', 'APF', 'APF']},
        {"name": "All 4 Robots: Distilled Decision Tree (Option C)", "controllers": ['Tree_Policy', 'Tree_Policy', 'Tree_Policy', 'Tree_Policy']},
        {"name": "All 4 Robots: Flat RL Neural Policy", "controllers": ['Flat_RL', 'Flat_RL', 'Flat_RL', 'Flat_RL']},
    ]
    current_mode_idx = 0

    def init_controllers(mode_idx):
        types = modes[mode_idx]["controllers"]
        return [create_ctrl(types[i], core, i, sensors, tree=tree) for i in range(4)]

    ctrls = init_controllers(current_mode_idx)

    print("=" * 70)
    print("UNIBOTS REAL-TIME MULTI-CONTROLLER SIMULATOR")
    print("Active Mode: " + modes[current_mode_idx]["name"])
    print("Controls:")
    print("  'M' : Cycle through all 7 matchup modes (2v2 and Isolated)")
    print("  'R' : Reset match & re-scatter arena elements")
    print("=" * 70)

    running = True
    match_steps = 0
    max_steps = 5400 # 180s @ 30Hz

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    core.reset()
                    sensors.reset()
                    ctrls = init_controllers(current_mode_idx)
                    match_steps = 0
                    print("\n[Match Reset: Field Re-scattered!]")
                elif event.key == pygame.K_m:
                    current_mode_idx = (current_mode_idx + 1) % len(modes)
                    core.reset()
                    sensors.reset()
                    ctrls = init_controllers(current_mode_idx)
                    match_steps = 0
                    print(f"\n>>> MODE SWITCHED: {modes[current_mode_idx]['name']} <<<")

        active_controllers = modes[current_mode_idx]['controllers']

        for i in range(4):
            vx, vy, omega = ctrls[i].compute_cmd()
            core.robots[i].vx = vx
            core.robots[i].vy = vy
            core.robots[i].omega = omega

        core.step()
        vis.render(mode_title=modes[current_mode_idx]['name'], controller_tags=active_controllers)
        vis.tick(30)
        match_steps += 1

        if match_steps >= max_steps:
            print(f"\n================== Match Result (180s) | {modes[current_mode_idx]['name']} ==================")
            scores = [core.compute_game_points(r) for r in core.robots]
            for idx, r in enumerate(core.robots):
                print(f"Robot {r.id} ({r.color.capitalize()}) [{active_controllers[idx]}]: {scores[idx]} pts | Scored Atoms: {r.scored_atoms} | Held: {r.total_held_elements} | Penalties: {r.collision_penalty_count}")
            team_a_score = scores[0] + scores[1]
            team_b_score = scores[2] + scores[3]
            print(f"-> FINAL SCORE: Team Yellow/Orange [{active_controllers[0]}] = {team_a_score} pts | Team Purple/Green [{active_controllers[2]}] = {team_b_score} pts")
            print("========================================================================================\n")
            core.reset()
            sensors.reset()
            ctrls = init_controllers(current_mode_idx)
            match_steps = 0

    pygame.quit()

if __name__ == "__main__":
    main()
