import math
import numpy as np
from typing import Optional, Tuple
from simulation.core import ArenaCore, Robot, ARENA_SIZE, ROBOT_SIZE, MAX_LONGITUDINAL_SPEED, MAX_LATERAL_SPEED, MAX_ANGULAR_SPEED
from simulation.sensors import Sensors

class NavigationPlanner:
    """
    Classical Autonomous Navigation Controller (Embedded, Zero God-Eye):
    - Target Routing: Sourced exclusively from onboard 8-sector egocentric spatial belief memory.
    - Active Visual Search: When memory is empty, executes arena patrol sweep with oscillating camera pan.
    - Local Avoidance: Sonar rays (Left, Right, Rear) + Front Camera live obstacle rays (No oracle opponent tracking).
    - Holonomic Mecanum Velocity Mapping: Forward-biased with lateral strafe capability.
    """
    def __init__(self, core: ArenaCore, robot_id: int, sensors: Optional[Sensors] = None):
        self.core = core
        self.robot_id = robot_id
        self.sensors = sensors if sensors is not None else Sensors(core)
        
        # APF Tuning Parameters
        self.k_attract = 1.2
        self.k_repulse_robot = 45000000.0  # Strong repulsive potential barrier (~720N at 250mm)
        self.k_repulse_wall = 80000.0
        self.robot_danger_radius = 550.0 # mm
        self.wall_danger_margin = 250.0  # mm from arena wall

    def get_scoring_net_pos(self) -> Tuple[float, float]:
        """Returns the world coordinates of this robot's assigned scoring net opening."""
        r = self.core.robots[self.robot_id]
        half = ARENA_SIZE / 2.0
        if r.color == 'yellow': return (half, ARENA_SIZE - 50.0)
        elif r.color == 'purple': return (half, 50.0)
        elif r.color == 'orange': return (ARENA_SIZE - 50.0, half)
        elif r.color == 'green': return (50.0, half)
        return (half, half)

    def select_target(self) -> Tuple[float, float, bool]:
        """
        Target selection using STRICTLY onboard perception (NO God-Eye):
        1. If container is postulated full (>= 4 balls) or foraging time >= 20s, return to net.
        2. If elements are remembered in onboard belief memory, pick best reachable ball.
        3. If belief memory is empty, return an Active Visual Search waypoint (patrolling quadrant).
        Returns: (target_x, target_y, is_search_mode)
        """
        r = self.core.robots[self.robot_id]
        
        # Greedy Foraging Strategy:
        # Stay out in the field to collect up to 4-5 balls!
        postulated_held = self.sensors.postulated_held.get(self.robot_id, 0)
        
        # In final 45 seconds of match (match_time >= 135s), bank any held balls immediately!
        # (Takes ~8-12s navigation + 30s deposit, finishing cleanly before the 180s buzzer!)
        is_end_game = (self.core.elapsed_time >= 135.0) and (postulated_held >= 1)
        
        # High-Capacity Batching Strategy:
        # Avoid premature 30s dock freezes when holding only 1 ball.
        # Return when container has a solid batch (>= 4 balls) or after extended foraging (>= 40s with >= 2 balls)
        is_greedy_full = (postulated_held >= 4) or (r.active_collection_time >= 40.0 and postulated_held >= 2)
        if is_greedy_full or is_end_game:
            net_x, net_y = self.get_scoring_net_pos()
            return net_x, net_y, False

        # Query onboard spatial belief memory (populated only by front 150-deg camera)
        mem = self.sensors.memory.get(self.robot_id, {})
        best_cost = float('inf')
        best_target = None

        tot_red = r.scored_compounds['red'] + r.held_compounds['red']
        tot_green = r.scored_compounds['green'] + r.held_compounds['green']
        tot_blue = r.scored_compounds['blue'] + r.held_compounds['blue']
        min_compounds = min(tot_red, tot_green, tot_blue)
        
        for el_id, entry in mem.items():
            mem_x, mem_y, el_type = entry[0], entry[1], entry[2]
            dx = mem_x - r.x
            dy = mem_y - r.y
            dist = math.hypot(dx, dy)
            
            # Prioritize compounds, especially missing colors that complete triads (+4 extra bonus!)
            if el_type == 'red_compound' and tot_red == min_compounds:
                score_val = 8.0 # Triad-completing red!
            elif el_type == 'green_compound' and tot_green == min_compounds:
                score_val = 8.0 # Triad-completing green!
            elif el_type == 'blue_compound' and tot_blue == min_compounds:
                score_val = 8.0 # Triad-completing blue!
            elif 'compound' in el_type:
                score_val = 4.0 # Standard compound
            else:
                score_val = 2.0 # Atom
                
            cost = dist / score_val
            
            if cost < best_cost:
                best_cost = cost
                best_target = (mem_x, mem_y)

        if best_target is not None:
            return best_target[0], best_target[1], False

        # Memory is EMPTY: Expansive Wide-Arena Search Mode!
        # Sweeps all 4 quadrants and perimeter zones (radius modulating from 500mm to 950mm)
        center = ARENA_SIZE / 2.0
        search_radius = 700.0 + 250.0 * math.sin(r.active_collection_time * 0.15)
        patrol_angle = (self.robot_id * (math.pi / 2.0)) + (r.active_collection_time * 0.22)
        search_x = center + search_radius * math.cos(patrol_angle)
        search_y = center + search_radius * math.sin(patrol_angle)
        search_x = float(np.clip(search_x, 350.0, ARENA_SIZE - 350.0))
        search_y = float(np.clip(search_y, 350.0, ARENA_SIZE - 350.0))

        return search_x, search_y, True

    def compute_cmd(self, target: Optional[Tuple[float, float, bool]] = None) -> Tuple[float, float, float]:
        """
        Computes (vx, vy, omega) in local robot frame.
        - vx: Forward velocity (up to 500 mm/s)
        - vy: Lateral strafe velocity (up to 300 mm/s)
        - omega: Angular rotation to align front camera/intake with target
        """
        r = self.core.robots[self.robot_id]
        
        # 0. Update onboard spatial belief memory and depletion postulation
        if self.sensors is not None:
            self.sensors.update(self.robot_id)

        # If currently serving 10s penalty freeze, do not send commands
        if r.is_penalized:
            return 0.0, 0.0, 0.0

        if target is not None:
            target_x, target_y, is_search_mode = target
        else:
            target_x, target_y, is_search_mode = self.select_target()
        
        net_x, net_y = self.get_scoring_net_pos()
        is_docking_target = (math.hypot(target_x - net_x, target_y - net_y) < 50.0)

        # 1. Lead-Pursuit Predictive Ball Interception:
        nav_x, nav_y = target_x, target_y
        if not is_search_mode and not is_docking_target:
            mem = self.sensors.memory.get(self.robot_id, {})
            for el_id, entry in mem.items():
                if math.hypot(entry[0] - target_x, entry[1] - target_y) < 40.0:
                    if len(entry) >= 6:
                        b_vx, b_vy = entry[4], entry[5]
                        b_speed = math.hypot(b_vx, b_vy)
                        if b_speed > 25.0: # Ball is rolling/bouncing
                            d_ball = max(10.0, math.hypot(entry[0] - r.x, entry[1] - r.y))
                            t_intercept = min(1.2, d_ball / 420.0)
                            nav_x = float(np.clip(entry[0] + b_vx * t_intercept, 120.0, ARENA_SIZE - 120.0))
                            nav_y = float(np.clip(entry[1] + b_vy * t_intercept, 120.0, ARENA_SIZE - 120.0))
                    break

        # Attractive force towards navigation target
        dx = nav_x - r.x
        dy = nav_y - r.y
        dist_to_target = max(10.0, math.hypot(dx, dy))
        fx = (dx / dist_to_target) * 350.0 * self.k_attract
        fy = (dy / dist_to_target) * 350.0 * self.k_attract

        # 2. Obstacle Repulsion from Front Camera live rays (Type 1.0 = Robot detected in front)
        camera_readings = self.sensors.get_camera_readings(self.robot_id)
        # 5 pairs: [norm_dist, type]
        cam_angles = np.linspace(-self.sensors.camera_fov / 2.0, self.sensors.camera_fov / 2.0, 5)
        min_front_robot_dist = float('inf')
        for idx in range(5):
            norm_d = camera_readings[idx * 2]
            ctype = camera_readings[idx * 2 + 1]
            if ctype >= 0.95: # Robot detected in front FOV!
                dist_mm = (norm_d + 1.0) / 2.0 * self.sensors.camera_max_range
                min_front_robot_dist = min(min_front_robot_dist, dist_mm)
                if dist_mm < self.robot_danger_radius:
                    rep_mag = self.k_repulse_robot / max(50.0, dist_mm)**2
                    ray_ang = r.theta + cam_angles[idx]
                    fx -= math.cos(ray_ang) * rep_mag
                    fy -= math.sin(ray_ang) * rep_mag

                    # ColRegs Port-to-Port Tangential Evasion:
                    # Apply an orthogonal circulation force (+90 deg) causing oncoming robots
                    # to actively strafe laterally past each other, eliminating head-on collisions!
                    ortho_ang = ray_ang + math.pi / 2.0
                    fx += math.cos(ortho_ang) * (rep_mag * 0.75)
                    fy += math.sin(ortho_ang) * (rep_mag * 0.75)

        # 3. Obstacle Repulsion from Sonars (Left, Right, Rear)
        sonars = self.sensors.get_sonar_readings(self.robot_id)
        # [Left (+90 deg), Right (-90 deg), Rear (180 deg)]
        left_dist = (sonars[0] + 1.0) / 2.0 * self.sensors.sonar_max_range
        right_dist = (sonars[1] + 1.0) / 2.0 * self.sensors.sonar_max_range
        rear_dist = (sonars[2] + 1.0) / 2.0 * self.sensors.sonar_max_range

        # Left sonar obstacle: push right
        if left_dist < 550.0:
            rep = self.k_repulse_robot / max(40.0, left_dist)**2
            left_ang = r.theta + math.pi / 2.0
            fx -= math.cos(left_ang) * rep
            fy -= math.sin(left_ang) * rep

        # Right sonar obstacle: push left
        if right_dist < 550.0:
            rep = self.k_repulse_robot / max(40.0, right_dist)**2
            right_ang = r.theta - math.pi / 2.0
            fx -= math.cos(right_ang) * rep
            fy -= math.sin(right_ang) * rep

        # Rear sonar obstacle: push forward (prevent backing into obstacles)
        if rear_dist < 450.0:
            rep = self.k_repulse_robot / max(40.0, rear_dist)**2
            rear_ang = r.theta + math.pi
            fx -= math.cos(rear_ang) * rep
            fy -= math.sin(rear_ang) * rep

        # 4. Repulsive force from Arena walls (known perimeter bounds from odometry)
        # Mask wall repulsion for assigned scoring net when actively depositing!
        if not (is_docking_target and r.color == 'green'):
            if r.x < self.wall_danger_margin:
                fx += self.k_repulse_wall / max(10.0, r.x)
        if not (is_docking_target and r.color == 'orange'):
            if r.x > ARENA_SIZE - self.wall_danger_margin:
                fx -= self.k_repulse_wall / max(10.0, ARENA_SIZE - r.x)
            
        if not (is_docking_target and r.color == 'purple'):
            if r.y < self.wall_danger_margin:
                fy += self.k_repulse_wall / max(10.0, r.y)
        if not (is_docking_target and r.color == 'yellow'):
            if r.y > ARENA_SIZE - self.wall_danger_margin:
                fy -= self.k_repulse_wall / max(10.0, ARENA_SIZE - r.y)

        # 5. Heading Alignment & Square Perpendicular Docking Pre-Alignment:
        if is_docking_target:
            # Perpendicular heading facing square into the wall net:
            if r.color == 'yellow': dock_heading = math.pi / 2.0
            elif r.color == 'purple': dock_heading = -math.pi / 2.0
            elif r.color == 'orange': dock_heading = 0.0
            elif r.color == 'green': dock_heading = math.pi
            else: dock_heading = math.atan2(dy, dx)
            target_heading = dock_heading
        else:
            # Always align front face (camera & 150mm intake) smoothly towards target
            target_heading = math.atan2(dy, dx)

        angle_diff = (target_heading - r.theta + math.pi) % (2.0 * math.pi) - math.pi
        omega = float(np.clip(angle_diff * 3.5, -MAX_ANGULAR_SPEED, MAX_ANGULAR_SPEED))

        # 6. Convert global net force into local Mecanum velocity commands
        cos_t = math.cos(r.theta)
        sin_t = math.sin(r.theta)
        local_fx = fx * cos_t + fy * sin_t
        local_fy = -fx * sin_t + fy * cos_t

        # 7. Holonomic Terminal Guidance & Swath Centering:
        if is_search_mode:
            # Active field search: serpentine zig-zag strafe (+/- 120 mm/s)
            zigzag_strafe = 120.0 * math.sin(r.active_collection_time * 2.5)
            local_fy += zigzag_strafe
        elif is_docking_target:
            # Square Centerline Funneling (Dead center entry into 760mm net opening)
            half = ARENA_SIZE / 2.0
            if r.color == 'yellow': dock_strafe = -(half - r.x) * 1.8
            elif r.color == 'purple': dock_strafe = (half - r.x) * 1.8
            elif r.color == 'orange': dock_strafe = (half - r.y) * 1.8
            elif r.color == 'green': dock_strafe = -(half - r.y) * 1.8
            else: dock_strafe = 0.0
            local_fy += float(np.clip(dock_strafe, -MAX_LATERAL_SPEED, MAX_LATERAL_SPEED))
        else:
            # Terminal Cross-Track Intake Centering for balls:
            # If target ball is within 400mm, apply lateral strafe to center mouth over ball
            target_lx = dx * cos_t + dy * sin_t
            target_ly = -dx * sin_t + dy * cos_t
            if 0.0 < target_lx < 400.0 and abs(target_ly) < 140.0:
                centering_vy = float(np.clip(target_ly * 2.5, -MAX_LATERAL_SPEED, MAX_LATERAL_SPEED))
                local_fy += centering_vy
            else:
                # Multi-ball line sweep: if adjacent balls are in the front corridor, pull laterally
                mem = self.sensors.memory.get(self.robot_id, {})
                flank_pull = 0.0
                for el_id, entry in mem.items():
                    mx, my = entry[0], entry[1]
                    bdx = mx - r.x
                    bdy = my - r.y
                    lx = bdx * cos_t + bdy * sin_t
                    ly = -bdx * sin_t + bdy * cos_t
                    if 40.0 < lx < 600.0 and 20.0 < abs(ly) < 250.0:
                        flank_pull += math.copysign(min(80.0, 3500.0 / max(50.0, lx)), ly)
                local_fy += flank_pull

        # 8. Obstacle Deceleration & Active Evasive Strafe (Prevents coasting into obstacle robots)
        if min_front_robot_dist < 480.0:
            if min_front_robot_dist < 340.0:
                # Critical danger zone: active reverse backing to open distance
                rev_speed = -140.0 * (1.0 - min_front_robot_dist / 340.0)
                local_fx = min(local_fx, rev_speed)
                # Command maximum lateral evasion strafe (300 mm/s) to slip past oncoming robot
                strafe_dir = 1.0 if local_fy >= 0.0 else -1.0
                local_fy = strafe_dir * MAX_LATERAL_SPEED
            else:
                max_fwd = max(0.0, (min_front_robot_dist - 300.0) * 1.5)
                local_fx = min(local_fx, max_fwd)

        # If heading error is large, avoid fast reverse so held balls are not dumped accidentally
        if abs(angle_diff) > math.pi / 2.0:
            local_fx = max(-20.0, min(100.0, local_fx))

        # Mecanum speed clipping (forward is faster than strafe)
        vx = float(np.clip(local_fx, -MAX_LONGITUDINAL_SPEED, MAX_LONGITUDINAL_SPEED))
        vy = float(np.clip(local_fy, -MAX_LATERAL_SPEED, MAX_LATERAL_SPEED))

        return vx, vy, omega
