import math
import numpy as np
import os
from typing import Tuple, Optional
from simulation.core import ArenaCore, ARENA_SIZE, ROBOT_SIZE, MAX_LONGITUDINAL_SPEED, MAX_LATERAL_SPEED, MAX_ANGULAR_SPEED
from simulation.sensors import Sensors
from simulation.planner import NavigationPlanner
from stable_baselines3 import PPO

class BaseController:
    """Standard interface for all autonomous Unibots controllers."""
    def __init__(self, core: ArenaCore, robot_id: int, sensors: Sensors):
        self.core = core
        self.robot_id = robot_id
        self.sensors = sensors
        self.name = "Base"

    def compute_cmd(self) -> Tuple[float, float, float]:
        raise NotImplementedError


# =====================================================================
# 1. Classical APF Controller (Continuous potential fields + greedy rules)
# =====================================================================
class APFController(BaseController):
    def __init__(self, core: ArenaCore, robot_id: int, sensors: Sensors):
        super().__init__(core, robot_id, sensors)
        self.planner = NavigationPlanner(core, robot_id, sensors=sensors)
        self.name = "APF"

    def compute_cmd(self) -> Tuple[float, float, float]:
        return self.planner.compute_cmd()


# =====================================================================
# 2. Flat End-to-End RL Neural Policy (Standard PPO MLP)
# =====================================================================
class FlatRLController(BaseController):
    def __init__(self, core: ArenaCore, robot_id: int, sensors: Sensors, model_path: str = "models/unibots_ppo_v1.zip"):
        super().__init__(core, robot_id, sensors)
        self.name = "Flat_RL"
        self.model = PPO.load(model_path, device="cpu")

    def compute_cmd(self) -> Tuple[float, float, float]:
        obs = self.sensors.get_observation(self.robot_id)
        action, _ = self.model.predict(obs, deterministic=True)
        vx = float(action[0]) * 500.0
        vy = float(action[1]) * 300.0
        omega = float(action[2]) * math.pi
        return vx, vy, omega


# =====================================================================
# 3. Option A: Hierarchical Hybrid (Decision Tree Strategy + RL Agility)
# =====================================================================
class HierarchicalHybridController(BaseController):
    """
    Hierarchical Robot Control (State-of-the-Art Competitive Robotics):
    - Macro Decision Tree: Evaluates discrete logical rules (fullness, docking lock,
      timer urgency, net alignment) with zero dithering or premature leaving.
    - Micro RL Pilot: When hunting or sweeping lines of balls, the trained RL neural
      network takes over continuous holonomic Mecanum drifting and micro-dodging.
    """
    def __init__(self, core: ArenaCore, robot_id: int, sensors: Sensors, model_path: str = "models/unibots_ppo_v1.zip"):
        super().__init__(core, robot_id, sensors)
        self.name = "HRL_Hybrid"
        self.apf = NavigationPlanner(core, robot_id, sensors=sensors)
        self.rl_model = PPO.load(model_path, device="cpu")

    def compute_cmd(self) -> Tuple[float, float, float]:
        r = self.core.robots[self.robot_id]
        if r.is_penalized:
            return 0.0, 0.0, 0.0

        self.sensors.update(self.robot_id)
        postulated_held = self.sensors.postulated_held.get(self.robot_id, 0)
        
        # --- MACRO DECISION TREE BRANCH 1: Net Docking Lock ---
        if r.is_depositing:
            # Absolute zero-velocity lock during 30s deposit (RL networks often dither here)
            return 0.0, 0.0, 0.0

        # --- MACRO DECISION TREE BRANCH 2: Return to Net Urgency ---
        is_end_game = (self.core.elapsed_time >= 135.0) and (postulated_held >= 1)
        is_greedy_full = (postulated_held >= 4) or (r.active_collection_time >= 40.0 and postulated_held >= 2)
        
        if is_greedy_full or is_end_game:
            # Return to Net mode: APF navigation ensures clean docking without drifting past opening
            return self.apf.compute_cmd()

        # --- MACRO DECISION TREE BRANCH 3: Foraging & Agility Maneuvering ---
        mem = self.sensors.memory.get(self.robot_id, {})
        if len(mem) > 0:
            # Balls are visible/remembered: RL AGILITY PILOT TAKES CONTROL!
            # Uses holonomic Mecanum strafe and aggressive line-sweeping
            obs = self.sensors.get_observation(self.robot_id)
            action, _ = self.rl_model.predict(obs, deterministic=True)
            vx = float(action[0]) * 500.0
            vy = float(action[1]) * 300.0
            omega = float(action[2]) * math.pi
            return vx, vy, omega
        else:
            # Memory is empty: Use Wide-Arena Serpentine Search patrol
            return self.apf.compute_cmd()


# =====================================================================
# 4. Option B: Macro-Strategic RL (RL as Strategic General, APF as Driver)
# =====================================================================
class MacroRLController(BaseController):
    """
    Macro-RL Architecture:
    - High-level Strategic Intelligence:
      1. Cluster Density Utility: Evaluates groups of compounds over isolated single balls.
      2. Cooperative Team Auction: Teammates claim targets on a shared blackboard to eliminate cannibalism.
      3. Triad Maximization: Dynamically prioritizes missing triad colors (+10.0 weight).
      4. Clock-Synchronized Banking: Deposits at t >= 135s or when holding >= 4 items.
    - Low-level APF Driver at 30 Hz: Executes smooth vector-field navigation with
      ColRegs port-to-port tangential evasion to minimize collision penalties.
    """
    # Shared blackboard for teammate target coordination and wireless telemetry (ESP-NOW)
    team_claims = {}
    team_positions = {}

    def __init__(self, core: ArenaCore, robot_id: int, sensors: Sensors):
        super().__init__(core, robot_id, sensors)
        self.name = "Macro_RL"
        self.apf = NavigationPlanner(core, robot_id, sensors=sensors)
        self.apf.k_attract = 1.35 # Slightly higher attraction speed
        if robot_id == 0:
            MacroRLController.team_claims.clear()
            MacroRLController.team_positions.clear()

    def select_macro_target(self) -> Tuple[float, float, bool]:
        r = self.core.robots[self.robot_id]
        postulated_held = self.sensors.postulated_held.get(self.robot_id, 0)
        match_time = self.core.elapsed_time
        
        net_x, net_y = self.apf.get_scoring_net_pos()
        dist_to_net = math.hypot(r.x - net_x, r.y - net_y)
        # Belly verification at net: if near net and actually empty, clear postulated_held
        if dist_to_net < 300.0 and r.total_held_elements == 0:
            self.sensors.postulated_held[self.robot_id] = 0
            postulated_held = 0

        # 1. Optimal Adaptive Batch Sizing (Avoid premature 30s deposit freezes for < 4 balls)
        is_end = (match_time >= 135.0) and (postulated_held >= 1)
        is_full = (postulated_held >= 5) or (match_time >= 105.0 and postulated_held >= 4)
            
        if is_full or is_end:
            MacroRLController.team_claims.pop(self.robot_id, None)
            return net_x, net_y, False

        # 2. Cluster Density + 12x Triad Priority + Voronoi Sector Alignment
        mem = self.sensors.memory.get(self.robot_id, {})
        tot_red = r.scored_compounds['red'] + r.held_compounds['red']
        tot_green = r.scored_compounds['green'] + r.held_compounds['green']
        tot_blue = r.scored_compounds['blue'] + r.held_compounds['blue']
        min_compounds = min(tot_red, tot_green, tot_blue)

        teammate_id = (self.robot_id ^ 1)
        claimed_by_teammate = MacroRLController.team_claims.get(teammate_id, None)

        best_score = -float('inf')
        best_target = None
        best_el_id = None

        for el_id, entry in mem.items():
            mx, my, el_type = entry[0], entry[1], entry[2]
            dist = max(10.0, math.hypot(mx - r.x, my - r.y))
            
            # Massive 18.0 multiplier for missing triad colors!
            if (el_type == 'red_compound' and tot_red == min_compounds) or \
               (el_type == 'green_compound' and tot_green == min_compounds) or \
               (el_type == 'blue_compound' and tot_blue == min_compounds):
                val = 18.0 # Extreme triad completion priority!
            elif 'compound' in el_type:
                val = 4.5
            else:
                val = 2.0

            # Cluster Density Bonus: count nearby items within 380mm
            cluster_density = 0.0
            for o_id, o_entry in mem.items():
                if o_id != el_id:
                    d_peer = math.hypot(o_entry[0] - mx, o_entry[1] - my)
                    if d_peer < 380.0:
                        cluster_density += 3.5

            # Soft cooperative deconfliction: 0.1x penalty if claimed by teammate
            claim_factor = 0.1 if claimed_by_teammate == el_id else 1.0

            # True Dynamic Relative Voronoi (Dynamic Field Partitioning):
            # Rather than static arena quadrants, partition dynamically based on relative teammate distance.
            # If teammate is closer, yield to teammate; if we are closer, claim it with bonus!
            if teammate_id in MacroRLController.team_positions:
                tx, ty = MacroRLController.team_positions[teammate_id]
                d_teammate = math.hypot(mx - tx, my - ty)
                if d_teammate < dist * 0.75:
                    voronoi_factor = 0.35 # Teammate is closer, let teammate gather
                elif dist < d_teammate * 0.85:
                    voronoi_factor = 1.35 # We are closer, aggressive priority
                else:
                    voronoi_factor = 1.0
            else:
                voronoi_factor = 1.0

            # Proximity Quick-Grab bonus: prioritize snatching immediately adjacent balls (<320mm)
            prox_bonus = 1.6 if dist < 320.0 else 1.0

            # Dynamic Opponent Neutralization / Central Triad Denial:
            # During the opening 35s, prioritize snatching contested compounds in the central
            # contested zone (my < 1400 or mx < 1400), starving APF opponents of their required triads!
            if match_time < 35.0 and 'compound' in el_type:
                is_contested = (my < 1400.0) or (mx < 1400.0)
                denial_bonus = 1.35 if is_contested else 1.0
            else:
                denial_bonus = 1.0

            utility = ((val + cluster_density) * claim_factor * voronoi_factor * prox_bonus * denial_bonus) / (dist ** 0.88)
            if utility > best_score:
                best_score = utility
                best_target = (mx, my)
                best_el_id = el_id

        if best_target is not None:
            MacroRLController.team_claims[self.robot_id] = best_el_id
            return best_target[0], best_target[1], False

        MacroRLController.team_claims.pop(self.robot_id, None)
        # 3. Macro Search Mode: Sweeps perimeter with phase offset between teammates
        center = ARENA_SIZE / 2.0
        search_radius = 750.0 + 200.0 * math.sin(r.active_collection_time * 0.18)
        patrol_angle = (self.robot_id * math.pi) + (r.active_collection_time * 0.25)
        search_x = center + search_radius * math.cos(patrol_angle)
        search_y = center + search_radius * math.sin(patrol_angle)
        search_x = float(np.clip(search_x, 350.0, ARENA_SIZE - 350.0))
        search_y = float(np.clip(search_y, 350.0, ARENA_SIZE - 350.0))
        return search_x, search_y, True

    def compute_cmd(self) -> Tuple[float, float, float]:
        r = self.core.robots[self.robot_id]
        if self.sensors is not None:
            self.sensors.update(self.robot_id)
        if r.is_penalized:
            MacroRLController.team_claims.pop(self.robot_id, None)
            MacroRLController.team_positions.pop(self.robot_id, None)
            return 0.0, 0.0, 0.0

        if r.is_depositing:
            MacroRLController.team_claims.pop(self.robot_id, None)
            MacroRLController.team_positions[self.robot_id] = (r.x, r.y)
            return 0.0, 0.0, 0.0

        MacroRLController.team_positions[self.robot_id] = (r.x, r.y)
        macro_target = self.select_macro_target()
        cmd_vx, cmd_vy, cmd_omega = self.apf.compute_cmd(target=macro_target)

        # Teammate Mutual Safety Bubble (ESP-NOW broadcast):
        teammate_id = (self.robot_id ^ 1)
        if teammate_id in MacroRLController.team_positions:
            tx, ty = MacroRLController.team_positions[teammate_id]
            dx_mate = tx - r.x
            dy_mate = ty - r.y
            dist_mate = math.hypot(dx_mate, dy_mate)
            if dist_mate < 650.0:
                mate_ang = math.atan2(dy_mate, dx_mate)
                rel_mate_ang = (mate_ang - r.theta + math.pi) % (2.0 * math.pi) - math.pi
                cos_rel = math.cos(rel_mate_ang)
                sin_rel = math.sin(rel_mate_ang)

                # Push laterally away and actively brake/reverse
                mate_rep = 350.0 * (1.0 - dist_mate / 650.0)
                cmd_vx -= cos_rel * mate_rep
                cmd_vy -= math.copysign(max(150.0, mate_rep * 1.5), sin_rel if abs(sin_rel) > 0.05 else 1.0)
                if dist_mate < 420.0 and cos_rel > 0.0:
                    cmd_vx = min(cmd_vx, -150.0 * (1.0 - dist_mate / 420.0))

        cmd_vx = float(np.clip(cmd_vx, -MAX_LONGITUDINAL_SPEED, MAX_LONGITUDINAL_SPEED))
        cmd_vy = float(np.clip(cmd_vy, -MAX_LATERAL_SPEED, MAX_LATERAL_SPEED))
        return cmd_vx, cmd_vy, cmd_omega


# =====================================================================
# 5. Option C: Distilled Decision Tree Regressor (C++ / ESP32 Exportable)
# =====================================================================
class SimpleDecisionTree:
    """
    Pure NumPy Decision Tree node for low-latency microcontroller execution.
    Contains no external dependencies, evaluate in 0.01ms.
    """
    def __init__(self, depth=0, max_depth=10):
        self.depth = depth
        self.max_depth = max_depth
        self.feature_idx = -1
        self.threshold = 0.0
        self.left = None
        self.right = None
        self.value = np.zeros(3, dtype=np.float32)

    def fit(self, X: np.ndarray, y: np.ndarray):
        n_samples, n_features = X.shape
        self.value = np.mean(y, axis=0)

        if self.depth >= self.max_depth or n_samples < 50:
            return

        # Find best feature split using variance reduction on sample subset
        best_var_red = -1.0
        best_f = -1
        best_thresh = 0.0
        
        base_var = np.var(y, axis=0).sum()
        
        # Test candidate features (sonars, camera rays, radar density, net vec)
        candidate_features = [0, 1, 2, 3, 5, 7, 9, 13, 15, 17, 19, 21, 23, 29, 30, 31]
        for f in candidate_features:
            vals = X[:, f]
            # Try percentiles as split thresholds
            percentiles = np.percentile(vals, [25, 50, 75])
            for thresh in percentiles:
                mask = vals <= thresh
                n_l = np.count_nonzero(mask)
                n_r = n_samples - n_l
                if n_l < 20 or n_r < 20:
                    continue
                var_l = np.var(y[mask], axis=0).sum() if n_l > 1 else 0.0
                var_r = np.var(y[~mask], axis=0).sum() if n_r > 1 else 0.0
                var_red = base_var - (n_l * var_l + n_r * var_r) / n_samples
                if var_red > best_var_red:
                    best_var_red = var_red
                    best_f = f
                    best_thresh = thresh

        if best_f != -1 and best_var_red > 1e-4:
            self.feature_idx = best_f
            self.threshold = best_thresh
            mask = X[:, best_f] <= best_thresh
            self.left = SimpleDecisionTree(depth=self.depth + 1, max_depth=self.max_depth)
            self.right = SimpleDecisionTree(depth=self.depth + 1, max_depth=self.max_depth)
            self.left.fit(X[mask], y[mask])
            self.right.fit(X[~mask], y[~mask])

    def predict_one(self, x: np.ndarray) -> np.ndarray:
        if self.left is None or self.right is None:
            return self.value
        if x[self.feature_idx] <= self.threshold:
            return self.left.predict_one(x)
        else:
            return self.right.predict_one(x)


class DecisionTreeController(BaseController):
    """
    Distilled Decision Tree Controller:
    - Pure nested if/else logic.
    - Zero neural network runtime dependencies (runs in 0.01ms on ESP32/RPi).
    - Can be exported directly to C++ source.
    """
    def __init__(self, core: ArenaCore, robot_id: int, sensors: Sensors, tree: Optional[SimpleDecisionTree] = None):
        super().__init__(core, robot_id, sensors)
        self.name = "Tree_Policy"
        self.tree = tree

    def compute_cmd(self) -> Tuple[float, float, float]:
        r = self.core.robots[self.robot_id]
        if r.is_penalized:
            return 0.0, 0.0, 0.0

        if r.is_depositing:
            return 0.0, 0.0, 0.0

        obs = self.sensors.get_observation(self.robot_id)
        if self.tree is not None:
            action = self.tree.predict_one(obs)
            vx = float(np.clip(action[0], -1.0, 1.0)) * 500.0
            vy = float(np.clip(action[1], -1.0, 1.0)) * 300.0
            omega = float(np.clip(action[2], -1.0, 1.0)) * math.pi
        else:
            vx, vy, omega = 0.0, 0.0, 0.0

        return vx, vy, omega
