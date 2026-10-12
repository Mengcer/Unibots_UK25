import functools
import numpy as np
from pettingzoo import ParallelEnv
from gymnasium.spaces import Box
import math
from simulation.core import ArenaCore, ROBOT_SIZE, ARENA_SIZE

class UnibotsEnv(ParallelEnv):
    metadata = {"render_modes": ["human", "rgb_array"], "name": "unibots_v1"}

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        self.core = ArenaCore()
        from simulation.sensors import Sensors
        self.sensors = Sensors(self.core)
        
        self.possible_agents = [f"robot_{i}" for i in range(4)]
        self.agents = self.possible_agents[:]
        
        self.enable_curriculum = False # Keep full standard matches for tournament consistency
        
        # Combo tracking for line-sweeping captures
        self.last_capture_time = {agent: -100.0 for agent in self.possible_agents}
        self.consecutive_captures = {agent: 0 for agent in self.possible_agents}
        
        # Observations: 
        # - 3 Sonar distances (Left, Right, Rear)
        # - 10 Camera FOV live rays (5 rays x [dist, type])
        # - 16 Egocentric Spatial Memory Radar (8 sectors x [min_dist, density])
        # - 2 Local net direction vector [norm_dx, norm_dy]
        # - 1 Internal foraging time estimator
        # Total = 32 continuous features
        self.observation_spaces = {
            agent: Box(low=-1.0, high=1.0, shape=(32,), dtype=np.float32) for agent in self.possible_agents
        }
        
        # Action space: vx, vy, omega (normalized between -1 and 1)
        self.action_spaces = {
            agent: Box(low=-1.0, high=1.0, shape=(3,), dtype=np.float32) for agent in self.possible_agents
        }
        
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return self.observation_spaces[agent]

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return self.action_spaces[agent]

    def _get_obs(self):
        obs = {}
        for i, agent in enumerate(self.agents):
            obs[agent] = self.sensors.get_observation(i)
        return obs

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self.core.reset()
        self.sensors.reset()
        self.step_count = 0
        self.last_capture_time = {agent: -100.0 for agent in self.possible_agents}
        self.consecutive_captures = {agent: 0 for agent in self.possible_agents}
        
        # LYi / Street Fighter Save-State Curriculum Scenario Initialization:
        # Occasionally spawn directly into mid-game docking states to break sparse-reward bottleneck!
        if self.enable_curriculum and (options is None or options.get("curriculum", True)):
            mode = np.random.choice(["standard", "docking_drill", "scramble"], p=[0.50, 0.30, 0.20])
            if mode == "docking_drill":
                # Spawn robots near wall net with pre-collected atoms (drill the 30s docking sequence!)
                for i, r in enumerate(self.core.robots):
                    r.held_atoms = np.random.randint(4, 7)
                    r.active_collection_time = 45.0
                    # Position within 400mm of wall net, facing towards wall
                    if i == 0:
                        r.x, r.y, r.theta = 1250.0 + np.random.uniform(-150, 150), 300.0, -math.pi / 2.0
                    elif i == 1:
                        r.x, r.y, r.theta = 2200.0, 1250.0 + np.random.uniform(-150, 150), 0.0
                    elif i == 2:
                        r.x, r.y, r.theta = 1250.0 + np.random.uniform(-150, 150), 2200.0, math.pi / 2.0
                    else:
                        r.x, r.y, r.theta = 300.0, 1250.0 + np.random.uniform(-150, 150), math.pi
                self.step_count = np.random.randint(1500, 3000)
            elif mode == "scramble":
                # Mid-game state with partially scattered robots
                for r in self.core.robots:
                    r.x = np.random.uniform(400.0, 2100.0)
                    r.y = np.random.uniform(400.0, 2100.0)
                    r.theta = np.random.uniform(-math.pi, math.pi)
                    r.held_atoms = np.random.randint(1, 4)
                self.step_count = np.random.randint(1000, 2000)

        observations = self._get_obs()
        infos = {agent: {} for agent in self.agents}
        
        return observations, infos

    def step(self, actions):
        # Apply actions
        for i, agent in enumerate(self.agents):
            if agent in actions:
                action = actions[agent]
                self.core.robots[i].vx = float(action[0]) * 500.0 # max 500 mm/s forward
                self.core.robots[i].vy = float(action[1]) * 300.0 # max 300 mm/s lateral strafe (Mecanum factor)
                self.core.robots[i].omega = float(action[2]) * math.pi # max pi rad/s
                
        # Previous metrics for differential reward
        old_scores = [self.core.compute_game_points(r) for r in self.core.robots]
        old_collisions = [r.collision_penalty_count for r in self.core.robots]
        old_held = [r.total_held_elements for r in self.core.robots]
        old_depositing = [r.is_depositing for r in self.core.robots]

        # Step physics
        self.core.step()
        self.step_count += 1
        
        # New metrics
        new_scores = [self.core.compute_game_points(r) for r in self.core.robots]
        new_collisions = [r.collision_penalty_count for r in self.core.robots]
        new_held = [r.total_held_elements for r in self.core.robots]
        new_depositing = [r.is_depositing for r in self.core.robots]

        # Get observations and calculate rewards
        observations = self._get_obs()
        rewards = {}
        for i, agent in enumerate(self.agents):
            score_diff = new_scores[i] - old_scores[i]
            collision_diff = new_collisions[i] - old_collisions[i]
            held_diff = new_held[i] - old_held[i]
            
            # 1. Scoring reward for depositing items into the wall net (+25 per score point diff)
            r_score = score_diff * 25.0
            
            # Upfront Docking Initiation Credit:
            # Solves the gamma=0.99 discount trap over the 900-step (30s) deposit duration.
            # Gives an immediate positive gradient to PPO the instant it drives into the dock!
            r_dock_init = 0.0
            if (not old_depositing[i]) and new_depositing[i] and old_held[i] > 0:
                r_dock_init = float(old_held[i]) * 15.0 + 25.0
            
            # High-Capacity Batch Bonus: Strongly reward greediness (collecting 4-6 balls before docking)
            # Depositing 5-6 balls in one 30s dock maximizes match time efficiency!
            r_batch = 0.0
            if score_diff > 0 and old_held[i] >= 4:
                r_batch = float(old_held[i]) * 10.0 # +40 to +60 bonus for high-capacity batch delivery!
                # Time efficiency bonus (Street Fighter inspiration: extra reward for scoring with remaining time)
                remaining_fraction = max(0.0, (5400 - self.step_count) / 5400.0)
                r_batch += remaining_fraction * 15.0
            
            # 2. Ingesting balls with COMBO / LINE-SWEEP bonus multiplier
            r_held = 0.0
            if held_diff > 0:
                current_time = self.step_count * (1.0 / 30.0)
                dt_capture = current_time - self.last_capture_time[agent]
                self.last_capture_time[agent] = current_time
                
                # If balls ingested in quick succession (< 2.5s), increment sweep combo!
                if dt_capture < 2.5:
                    self.consecutive_captures[agent] += held_diff
                else:
                    self.consecutive_captures[agent] = held_diff
                    
                combo = min(4, self.consecutive_captures[agent])
                # Escalating reward encourages continuous straight line sweeping!
                r_held = held_diff * (10.0 + 5.0 * combo)
                
                # Bonus for using Mecanum lateral strafe (Vy) during ingestion
                r_held += float(abs(self.core.robots[i].vy) / 300.0) * 4.0
            elif held_diff < 0 and score_diff == 0:
                # Penalty for accidentally dumping balls out front by reversing
                r_held = held_diff * 10.0
                self.consecutive_captures[agent] = 0
            
            # 3. Collision reset penalty (-30 for causing 10s freeze reset)
            r_collision = -collision_diff * 30.0
            
            # 4. Small penalty while frozen in starting box
            r_freeze = -0.05 if self.core.robots[i].is_penalized else 0.0
            
            # 5. Bonus during 30s deposit sequence to encourage staying docked
            r_deposit = 0.15 if self.core.robots[i].is_depositing else 0.0

            # 6. Motor Jerk / Slew Smoothness Penalty (protects toy DC motors from stall current spikes)
            r_smooth = -0.005 * min(1.0, self.core.robots[i].last_jerk / 1500.0)
            
            # Calibrated step penalty (-0.001 instead of harsh -0.01)
            rewards[agent] = float(r_score + r_batch + r_dock_init + r_held + r_collision + r_freeze + r_deposit + r_smooth - 0.001)

        # 180 seconds at 30Hz = 5400 steps per match
        done = self.step_count >= 5400
        terminations = {agent: False for agent in self.agents}
        truncations = {agent: done for agent in self.agents}
        infos = {
            agent: {
                "score": new_scores[i],
                "collisions": new_collisions[i],
                "held": self.core.robots[i].total_held_elements,
                "is_full": self.core.robots[i].is_container_full,
                "is_depositing": self.core.robots[i].is_depositing,
            }
            for i, agent in enumerate(self.agents)
        }
        
        return observations, rewards, terminations, truncations, infos

    def render(self):
        pass
