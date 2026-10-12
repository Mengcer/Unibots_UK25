import os
import time
import pickle
import numpy as np
from simulation.core import ArenaCore
from simulation.sensors import Sensors
from simulation.planner import NavigationPlanner
from simulation.controllers import SimpleDecisionTree, DecisionTreeController, MacroRLController

def collect_training_samples(num_samples: int = 50000):
    print(f"[Phase 1] Collecting {num_samples:,} samples from MacroRL champion policy for Decision Tree...")
    core = ArenaCore()
    sensors = Sensors(core)
    ctrls = [MacroRLController(core, i, sensors=sensors) for i in range(4)]
    
    observations = []
    actions = []
    samples = 0
    match_steps = 0
    t0 = time.time()
    
    while samples < num_samples:
        for i in range(4):
            obs = sensors.get_observation(i)
            vx, vy, omega = ctrls[i].compute_cmd()
            norm_action = [
                float(np.clip(vx / 500.0, -1.0, 1.0)),
                float(np.clip(vy / 300.0, -1.0, 1.0)),
                float(np.clip(omega / 3.14159, -1.0, 1.0))
            ]
            observations.append(obs)
            actions.append(norm_action)
            core.robots[i].vx = vx
            core.robots[i].vy = vy
            core.robots[i].omega = omega
            samples += 1
            if samples >= num_samples:
                break
        core.step()
        match_steps += 1
        if match_steps >= 5400:
            core.reset()
            sensors.reset()
            ctrls = [MacroRLController(core, i, sensors=sensors) for i in range(4)]
            match_steps = 0
            
    print(f"-> Collected {len(observations):,} pairs in {time.time() - t0:.1f}s!")
    return np.array(observations, dtype=np.float32), np.array(actions, dtype=np.float32)

def export_to_cpp(node: SimpleDecisionTree, f, indent=4):
    """Recursively exports a decision tree node to C++ code."""
    spaces = " " * indent
    if node.left is None or node.right is None:
        f.write(f"{spaces}action[0] = {node.value[0]:.4f}f;\n")
        f.write(f"{spaces}action[1] = {node.value[1]:.4f}f;\n")
        f.write(f"{spaces}action[2] = {node.value[2]:.4f}f;\n")
        f.write(f"{spaces}return;\n")
    else:
        f.write(f"{spaces}if (obs[{node.feature_idx}] <= {node.threshold:.4f}f) {{\n")
        export_to_cpp(node.left, f, indent + 4)
        f.write(f"{spaces}}} else {{\n")
        export_to_cpp(node.right, f, indent + 4)
        f.write(f"{spaces}}}\n")

def generate_cpp_header(tree: SimpleDecisionTree, out_path: str = "firmware/esp32_policy_tree.hpp"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("// =====================================================================\n")
        f.write("// Auto-Generated Unibots Autonomous Policy Tree (C++ for ESP32 / Arduino)\n")
        f.write("// Zero external dependencies, executes in ~0.01 ms on microcontrollers\n")
        f.write("// =====================================================================\n\n")
        f.write("#ifndef ESP32_POLICY_TREE_HPP\n")
        f.write("#define ESP32_POLICY_TREE_HPP\n\n")
        f.write("inline void evaluate_policy_tree(const float obs[32], float action[3]) {\n")
        export_to_cpp(tree, f, indent=4)
        f.write("}\n\n")
        f.write("#endif // ESP32_POLICY_TREE_HPP\n")
    print(f"-> Generated C++ microcontroller header at: {out_path}")

def main():
    X, y = collect_training_samples(60000)
    print("\n[Phase 2] Fitting Multi-Output Decision Tree (max_depth=9)...")
    t0 = time.time()
    tree = SimpleDecisionTree(max_depth=9)
    tree.fit(X, y)
    print(f"-> Decision Tree training complete in {time.time() - t0:.1f}s!")
    
    os.makedirs("models", exist_ok=True)
    with open("models/decision_tree_policy.pkl", "wb") as f:
        pickle.dump(tree, f)
    print("-> Saved Python model to models/decision_tree_policy.pkl")
    
    # Generate pure C++ header for physical robot hardware
    generate_cpp_header(tree, "firmware/esp32_policy_tree.hpp")
    
    # Quick 1-match benchmark
    core = ArenaCore()
    sensors = Sensors(core)
    controllers = [DecisionTreeController(core, i, sensors=sensors, tree=tree) for i in range(4)]
    for _ in range(5400):
        for i in range(4):
            vx, vy, omega = controllers[i].compute_cmd()
            core.robots[i].vx = vx
            core.robots[i].vy = vy
            core.robots[i].omega = omega
        core.step()
    scores = [core.compute_game_points(r) for r in core.robots]
    pens = [r.collision_penalty_count for r in core.robots]
    print(f"\n[Decision Tree Match Result]: Scores = {scores} (Avg: {np.mean(scores):.1f} pts) | Penalties = {pens}")

if __name__ == "__main__":
    main()
