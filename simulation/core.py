import numpy as np
import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

# Arena constants
ARENA_SIZE = 2500.0
ROBOT_SIZE = 200.0
ROBOT_HALF = ROBOT_SIZE / 2.0
ROBOT_RADIUS = ROBOT_HALF * math.sqrt(2) # circumscribed radius ~141.4mm
ATOM_RADIUS = 10.0
COMPOUND_RADIUS = 15.0 # tip-to-tip 30mm

# Intake opening parameters
INTAKE_WIDTH = 150.0 # 150mm opening on front face
INTAKE_HALF_WIDTH = INTAKE_WIDTH / 2.0

# Physical capacity limit of the internal C-container cavity (approximately 6-7 balls max)
MAX_CONTAINER_CAPACITY = 6

# Mecanum kinematics limits
MAX_LONGITUDINAL_SPEED = 500.0  # mm/s forward/reverse
MAX_LATERAL_SPEED = 300.0       # mm/s strafing left/right (~60% efficiency due to 45 deg rollers)
MAX_ANGULAR_SPEED = math.pi     # rad/s

# Penalty & Deposit durations
PENALTY_FREEZE_SECONDS = 10.0
DEPOSIT_DURATION_SECONDS = 30.0 # Docking & depositing takes 30s

@dataclass
class GameElement:
    id: int
    type: str # 'atom', 'red_compound', 'green_compound', 'blue_compound'
    x: float
    y: float
    radius: float
    vx: float = 0.0
    vy: float = 0.0
    # Container tracking: if trapped inside a C-shaped robot container
    trapped_by_robot_id: Optional[int] = None
    scored: bool = False # permanently deposited in wall net

class Robot:
    def __init__(self, id: int, color: str, start_x: float, start_y: float, start_theta: float):
        self.id = id
        self.color = color
        self.start_x = start_x
        self.start_y = start_y
        self.start_theta = start_theta
        
        self.x = start_x
        self.y = start_y
        self.theta = start_theta
        
        self.vx = 0.0 # Local forward/backward commanded velocity
        self.vy = 0.0 # Local lateral strafe commanded velocity
        self.omega = 0.0 # Commanded angular velocity

        # Realistic Toy DC Motor Physics (130-size motor with ~1:48 gearbox)
        self.actual_vx = 0.0       # Actual physical speed with mechanical inertia
        self.actual_vy = 0.0
        self.actual_omega = 0.0
        self.motor_tau = 0.12      # 120 ms mechanical time constant (low torque / inertia)
        self.deadband_vel = 30.0   # mm/s: below ~6% PWM, static friction prevents motion
        self.deadband_omega = 0.15 # rad/s
        self.max_accel_lin = 1500.0 # mm/s^2: slew-rate limit prevents stall-current brownouts
        self.max_accel_ang = 4.0 * math.pi # rad/s^2
        self.last_jerk = 0.0       # Track rate of acceleration change for smoothness rewards
        
        self.held_atoms = 0
        self.held_compounds = {'red': 0, 'green': 0, 'blue': 0}
        self.scored_atoms = 0
        self.scored_compounds = {'red': 0, 'green': 0, 'blue': 0}
        self.collision_penalty_count = 0
        self.penalty_timer = 0.0  # Remaining seconds locked in starting box
        self.deposit_timer = 0.0  # Remaining seconds locked in net dock depositing (30s)

        # Odometry / Internal collection estimators (since no direct sensor tells if container is full)
        # Robot accumulates estimated distance travelled / active collection duration
        self.active_collection_time = 0.0

    @property
    def total_held_elements(self) -> int:
        return self.held_atoms + sum(self.held_compounds.values())

    @property
    def is_container_full(self) -> bool:
        return self.total_held_elements >= MAX_CONTAINER_CAPACITY

    @property
    def is_penalized(self) -> bool:
        return self.penalty_timer > 0.0

    @property
    def is_depositing(self) -> bool:
        return self.deposit_timer > 0.0

    @property
    def is_in_starting_box(self) -> bool:
        """Checks if robot center is within its designated starting zone tolerance."""
        return math.hypot(self.x - self.start_x, self.y - self.start_y) < 30.0

    def apply_collision_penalty(self):
        """Penalize robot: teleport back to start box and freeze for 10 seconds."""
        self.x = self.start_x
        self.y = self.start_y
        self.theta = self.start_theta
        self.vx = 0.0
        self.vy = 0.0
        self.omega = 0.0
        self.actual_vx = 0.0
        self.actual_vy = 0.0
        self.actual_omega = 0.0
        self.penalty_timer = PENALTY_FREEZE_SECONDS
        self.deposit_timer = 0.0
        self.active_collection_time = 0.0
        self.collision_penalty_count += 1

    def step(self, dt: float):
        # 1. If under 10s penalty freeze, count down and lock in place
        if self.penalty_timer > 0.0:
            self.penalty_timer = max(0.0, self.penalty_timer - dt)
            self.x = self.start_x
            self.y = self.start_y
            self.theta = self.start_theta
            self.vx = 0.0
            self.vy = 0.0
            self.omega = 0.0
            self.actual_vx = 0.0
            self.actual_vy = 0.0
            self.actual_omega = 0.0
            return

        # 2. If actively docked and depositing balls (30 seconds duration)
        if self.deposit_timer > 0.0:
            self.deposit_timer = max(0.0, self.deposit_timer - dt)
            self.vx = 0.0
            self.vy = 0.0
            self.omega = 0.0
            self.actual_vx = 0.0
            self.actual_vy = 0.0
            self.actual_omega = 0.0
            return

        # Track active collection time (used as an internal estimator of container fullness)
        self.active_collection_time += dt

        # 3. Mecanum drive velocity limits
        eff_vx = float(np.clip(self.vx, -MAX_LONGITUDINAL_SPEED, MAX_LONGITUDINAL_SPEED))
        eff_vy = float(np.clip(self.vy, -MAX_LATERAL_SPEED, MAX_LATERAL_SPEED))
        eff_omega = float(np.clip(self.omega, -MAX_ANGULAR_SPEED, MAX_ANGULAR_SPEED))

        # 4. Realistic DC Motor Deadband (stiction below minimum PWM)
        target_vx = 0.0 if abs(eff_vx) < self.deadband_vel else eff_vx
        target_vy = 0.0 if abs(eff_vy) < self.deadband_vel else eff_vy
        target_omega = 0.0 if abs(eff_omega) < self.deadband_omega else eff_omega

        # 5. Slew-rate rate limiting (finite acceleration prevents motor stall spikes)
        max_d_lin = self.max_accel_lin * dt
        max_d_ang = self.max_accel_ang * dt
        target_vx = np.clip(target_vx, self.actual_vx - max_d_lin, self.actual_vx + max_d_lin)
        target_vy = np.clip(target_vy, self.actual_vy - max_d_lin, self.actual_vy + max_d_lin)
        target_omega = np.clip(target_omega, self.actual_omega - max_d_ang, self.actual_omega + max_d_ang)

        # 6. 1st-order mechanical lag (motor inertia filter)
        decay = math.exp(-dt / self.motor_tau)
        prev_vx = self.actual_vx
        self.actual_vx = float(decay * self.actual_vx + (1.0 - decay) * target_vx)
        self.actual_vy = float(decay * self.actual_vy + (1.0 - decay) * target_vy)
        self.actual_omega = float(decay * self.actual_omega + (1.0 - decay) * target_omega)

        self.last_jerk = abs((self.actual_vx - prev_vx) / dt)

        # Convert actual velocities to global frame
        global_vx = self.actual_vx * math.cos(self.theta) - self.actual_vy * math.sin(self.theta)
        global_vy = self.actual_vx * math.sin(self.theta) + self.actual_vy * math.cos(self.theta)
        
        self.x += global_vx * dt
        self.y += global_vy * dt
        self.theta += self.actual_omega * dt
        
        # Keep theta in [-pi, pi]
        self.theta = (self.theta + math.pi) % (2.0 * math.pi) - math.pi

    def get_corners(self) -> List[Tuple[float, float]]:
        """Returns 4 outer corners in global coordinates."""
        cos_t = math.cos(self.theta)
        sin_t = math.sin(self.theta)
        local_pts = [
            (ROBOT_HALF, -ROBOT_HALF),
            (ROBOT_HALF, ROBOT_HALF),
            (-ROBOT_HALF, ROBOT_HALF),
            (-ROBOT_HALF, -ROBOT_HALF)
        ]
        corners = []
        for lx, ly in local_pts:
            gx = self.x + lx * cos_t - ly * sin_t
            gy = self.y + lx * sin_t + ly * cos_t
            corners.append((gx, gy))
        return corners

    def get_c_shape_corners(self) -> List[Tuple[float, float]]:
        """
        Returns the 8 vertices defining the physical C-shaped container contour in global coordinates.
        Outer bounds: 200x200mm square.
        Front opening: 150mm wide mouth along the front face (+X).
        Solid walls: 25mm left wall, 25mm right wall, 20mm rear wall.
        """
        cos_t = math.cos(self.theta)
        sin_t = math.sin(self.theta)
        wall_thick = 20.0
        local_pts = [
            (ROBOT_HALF, ROBOT_HALF),                               # 1. Front-left outer tip
            (-ROBOT_HALF, ROBOT_HALF),                              # 2. Back-left outer corner
            (-ROBOT_HALF, -ROBOT_HALF),                             # 3. Back-right outer corner
            (ROBOT_HALF, -ROBOT_HALF),                              # 4. Front-right outer tip
            (ROBOT_HALF, -INTAKE_HALF_WIDTH),                       # 5. Front-right opening mouth
            (-ROBOT_HALF + wall_thick, -INTAKE_HALF_WIDTH),         # 6. Cavity back-right
            (-ROBOT_HALF + wall_thick, INTAKE_HALF_WIDTH),          # 7. Cavity back-left
            (ROBOT_HALF, INTAKE_HALF_WIDTH),                        # 8. Front-left opening mouth
        ]
        corners = []
        for lx, ly in local_pts:
            gx = self.x + lx * cos_t - ly * sin_t
            gy = self.y + lx * sin_t + ly * cos_t
            corners.append((gx, gy))
        return corners

class ArenaCore:
    def __init__(self):
        self.size = ARENA_SIZE
        self.dt = 1.0 / 30.0 # 30 Hz simulation
        self.reset()

    def reset(self):
        self.elapsed_time = 0.0
        self.robots = [
            Robot(0, 'yellow', ARENA_SIZE / 2.0, ARENA_SIZE - ROBOT_HALF, -math.pi / 2.0),
            Robot(1, 'orange', ARENA_SIZE - ROBOT_HALF, ARENA_SIZE / 2.0, math.pi),
            Robot(2, 'purple', ARENA_SIZE / 2.0, ROBOT_HALF, math.pi / 2.0),
            Robot(3, 'green', ROBOT_HALF, ARENA_SIZE / 2.0, 0.0)
        ]

        self.elements: List[GameElement] = []
        element_id = 0
        
        def random_safe_pos():
            margin = 350.0
            return random.uniform(margin, ARENA_SIZE - margin), random.uniform(margin, ARENA_SIZE - margin)

        # 24 Atoms (steel balls)
        for _ in range(24):
            x, y = random_safe_pos()
            self.elements.append(GameElement(element_id, 'atom', x, y, ATOM_RADIUS))
            element_id += 1
            
        # 21 Compounds (7 Red, 7 Green, 7 Blue)
        for color in ['red_compound', 'green_compound', 'blue_compound']:
            for _ in range(7):
                x, y = random_safe_pos()
                self.elements.append(GameElement(element_id, color, x, y, COMPOUND_RADIUS))
                element_id += 1

    def step(self):
        self.elapsed_time += self.dt
        # 1. Update robot positions (incorporating 10s penalty freeze, 30s deposit, and Mecanum limits)
        for r in self.robots:
            r.step(self.dt)
            r.x = float(np.clip(r.x, ROBOT_HALF, ARENA_SIZE - ROBOT_HALF))
            r.y = float(np.clip(r.y, ROBOT_HALF, ARENA_SIZE - ROBOT_HALF))
            
        # 2. Inter-robot collisions & Rule Penalty Logic
        robots_to_penalize = set()
        for i in range(len(self.robots)):
            for j in range(i + 1, len(self.robots)):
                r1 = self.robots[i]
                r2 = self.robots[j]
                dx = r2.x - r1.x
                dy = r2.y - r1.y
                dist = math.hypot(dx, dy)
                if dist < ROBOT_SIZE:
                    r1_safe_in_box = r1.is_penalized and r1.is_in_starting_box
                    r2_safe_in_box = r2.is_penalized and r2.is_in_starting_box

                    if r1_safe_in_box and not r2_safe_in_box:
                        robots_to_penalize.add(j)
                    elif r2_safe_in_box and not r1_safe_in_box:
                        robots_to_penalize.add(i)
                    elif not r1_safe_in_box and not r2_safe_in_box:
                        robots_to_penalize.add(i)
                        robots_to_penalize.add(j)

        for robot_idx in robots_to_penalize:
            for el in self.elements:
                if el.trapped_by_robot_id == robot_idx:
                    el.trapped_by_robot_id = None
                    el.vx = random.uniform(-50, 50)
                    el.vy = random.uniform(-50, 50)
            self.robots[robot_idx].apply_collision_penalty()

        # 3. Game element physics: free balls bounce off arena walls
        for el in self.elements:
            if el.scored: continue
            
            if el.trapped_by_robot_id is None:
                el.x += el.vx * self.dt
                el.y += el.vy * self.dt
                el.vx *= 0.90
                el.vy *= 0.90
                
                if el.x - el.radius < 0:
                    el.x = el.radius
                    el.vx = -el.vx * 0.7
                elif el.x + el.radius > ARENA_SIZE:
                    el.x = ARENA_SIZE - el.radius
                    el.vx = -el.vx * 0.7
                    
                if el.y - el.radius < 0:
                    el.y = el.radius
                    el.vy = -el.vy * 0.7
                elif el.y + el.radius > ARENA_SIZE:
                    el.y = ARENA_SIZE - el.radius
                    el.vy = -el.vy * 0.7

        # 4. C-Shaped Container Physics & Ball Interaction:
        wall_thick = 20.0
        for r in self.robots:
            cos_t = math.cos(r.theta)
            sin_t = math.sin(r.theta)

            r_global_vx = r.vx * cos_t - r.vy * sin_t
            r_global_vy = r.vx * sin_t + r.vy * cos_t

            # A. Update balls already TRAPPED in this robot's C-container
            trapped_elements = [el for el in self.elements if el.trapped_by_robot_id == r.id and not el.scored]
            
            for idx, el in enumerate(trapped_elements):
                dx = el.x - r.x
                dy = el.y - r.y
                local_x = dx * cos_t + dy * sin_t
                local_y = -dx * sin_t + dy * cos_t

                # If robot reverses fast, balls slide forward out of front opening
                if r.vx < -40.0:
                    slide_speed = -r.vx * 1.0
                    local_x += slide_speed * self.dt
                    if local_x > ROBOT_HALF + el.radius:
                        el.trapped_by_robot_id = None
                        el.vx = r_global_vx + cos_t * 150.0
                        el.vy = r_global_vy + sin_t * 150.0
                        el.x = r.x + (ROBOT_HALF + el.radius + 5.0) * cos_t - local_y * sin_t
                        el.y = r.y + (ROBOT_HALF + el.radius + 5.0) * sin_t + local_y * cos_t
                        continue
                else:
                    # Target resting slot inside C-container cavity (2 columns of 3 rows)
                    row = idx // 2
                    col = idx % 2
                    target_local_x = -ROBOT_HALF + wall_thick + 25.0 + row * 35.0
                    target_local_y = -30.0 if col == 0 else 30.0
                    local_x += (target_local_x - local_x) * min(1.0, 15.0 * self.dt)
                    local_y += (target_local_y - local_y) * min(1.0, 15.0 * self.dt)

                el.x = r.x + local_x * cos_t - local_y * sin_t
                el.y = r.y + local_x * sin_t + local_y * cos_t
                el.vx = r_global_vx
                el.vy = r_global_vy

            # B. Check FREE balls interacting with this robot:
            for el in self.elements:
                if el.scored or el.trapped_by_robot_id is not None:
                    continue

                dx = el.x - r.x
                dy = el.y - r.y
                dist = math.hypot(dx, dy)
                if dist > ROBOT_RADIUS + el.radius + 30.0:
                    continue

                local_x = dx * cos_t + dy * sin_t
                local_y = -dx * sin_t + dy * cos_t

                can_accept = (r.total_held_elements < MAX_CONTAINER_CAPACITY) and not r.is_depositing and (r.vx >= -20.0)
                in_mouth_y = abs(local_y) <= (INTAKE_HALF_WIDTH - 2.0)

                # Intake mouth entry check:
                # If within 150mm opening width and touching/passing through front opening plane
                if can_accept and in_mouth_y and (-ROBOT_HALF + 30.0 <= local_x <= ROBOT_HALF + el.radius + 15.0):
                    el.trapped_by_robot_id = r.id
                    el.vx = r_global_vx
                    el.vy = r_global_vy
                    continue

                # Solid walls deflection check:
                # 1. Left wall: x in [-ROBOT_HALF, ROBOT_HALF], y in [INTAKE_HALF_WIDTH, ROBOT_HALF]
                # 2. Right wall: x in [-ROBOT_HALF, ROBOT_HALF], y in [-ROBOT_HALF, -INTAKE_HALF_WIDTH]
                # 3. Back wall: x in [-ROBOT_HALF, -ROBOT_HALF + wall_thick], y in [-INTAKE_HALF_WIDTH, INTAKE_HALF_WIDTH]
                # 4. If container is full or depositing: front mouth barrier
                solid_boxes = [
                    (-ROBOT_HALF, ROBOT_HALF, INTAKE_HALF_WIDTH, ROBOT_HALF),
                    (-ROBOT_HALF, ROBOT_HALF, -ROBOT_HALF, -INTAKE_HALF_WIDTH),
                    (-ROBOT_HALF, -ROBOT_HALF + wall_thick, -INTAKE_HALF_WIDTH, INTAKE_HALF_WIDTH)
                ]
                if not can_accept:
                    solid_boxes.append((ROBOT_HALF - 10.0, ROBOT_HALF, -INTAKE_HALF_WIDTH, INTAKE_HALF_WIDTH))

                for bx_min, bx_max, by_min, by_max in solid_boxes:
                    cx = float(np.clip(local_x, bx_min, bx_max))
                    cy = float(np.clip(local_y, by_min, by_max))
                    p_dx = local_x - cx
                    p_dy = local_y - cy
                    p_dist = math.hypot(p_dx, p_dy)

                    if p_dist < el.radius:
                        if p_dist < 1e-4:
                            d_left = local_y - by_min
                            d_right = by_max - local_y
                            d_back = local_x - bx_min
                            d_front = bx_max - local_x
                            min_d = min(d_left, d_right, d_back, d_front)
                            if min_d == d_left: nx, ny = 0.0, -1.0; pen = el.radius + d_left
                            elif min_d == d_right: nx, ny = 0.0, 1.0; pen = el.radius + d_right
                            elif min_d == d_back: nx, ny = -1.0, 0.0; pen = el.radius + d_back
                            else: nx, ny = 1.0, 0.0; pen = el.radius + d_front
                        else:
                            nx = p_dx / p_dist
                            ny = p_dy / p_dist
                            pen = el.radius - p_dist

                        local_x += nx * pen
                        local_y += ny * pen
                        el.x = r.x + local_x * cos_t - local_y * sin_t
                        el.y = r.y + local_x * sin_t + local_y * cos_t

                        gnx = nx * cos_t - ny * sin_t
                        gny = nx * sin_t + ny * cos_t
                        r_speed_normal = r_global_vx * gnx + r_global_vy * gny
                        bounce_speed = max(180.0, max(0.0, r_speed_normal) + 120.0)
                        el.vx = gnx * bounce_speed
                        el.vy = gny * bounce_speed
                        break

        # 5. Scoring & 30-Second Docking Deposit Logic:
        net_center = ARENA_SIZE / 2.0
        for r in self.robots:
            # Recalculate currently held elements inside C-container
            current_held_atoms = 0
            current_held_compounds = {'red': 0, 'green': 0, 'blue': 0}
            
            for el in self.elements:
                if el.trapped_by_robot_id == r.id and not el.scored:
                    if el.type == 'atom':
                        current_held_atoms += 1
                    elif el.type == 'red_compound':
                        current_held_compounds['red'] += 1
                    elif el.type == 'green_compound':
                        current_held_compounds['green'] += 1
                    elif el.type == 'blue_compound':
                        current_held_compounds['blue'] += 1

            r.held_atoms = current_held_atoms
            r.held_compounds = current_held_compounds

            # Check if robot is docked at assigned wall net (760mm wide opening)
            in_net_zone = False
            if r.color == 'yellow':
                in_net_zone = (r.y > ARENA_SIZE - ROBOT_SIZE) and (abs(r.x - net_center) <= 380)
            elif r.color == 'purple':
                in_net_zone = (r.y < ROBOT_SIZE) and (abs(r.x - net_center) <= 380)
            elif r.color == 'orange':
                in_net_zone = (r.x > ARENA_SIZE - ROBOT_SIZE) and (abs(r.y - net_center) <= 380)
            elif r.color == 'green':
                in_net_zone = (r.x < ROBOT_SIZE) and (abs(r.y - net_center) <= 380)

            # Trigger 30-Second Deposit Sequence if carrying balls into dock
            if in_net_zone and r.total_held_elements > 0 and not r.is_depositing:
                r.deposit_timer = DEPOSIT_DURATION_SECONDS
                r.active_collection_time = 0.0

            # When deposit sequence finishes (or while docked), empty container into scoring net
            if in_net_zone and r.deposit_timer <= 0.1 and r.total_held_elements > 0:
                for el in self.elements:
                    if el.trapped_by_robot_id == r.id and not el.scored:
                        el.scored = True
                        el.trapped_by_robot_id = None
                        if el.type == 'atom':
                            r.scored_atoms += 1
                        elif el.type == 'red_compound':
                            r.scored_compounds['red'] += 1
                        elif el.type == 'green_compound':
                            r.scored_compounds['green'] += 1
                        elif el.type == 'blue_compound':
                            r.scored_compounds['blue'] += 1
                r.held_atoms = 0
                r.held_compounds = {'red': 0, 'green': 0, 'blue': 0}

    def compute_game_points(self, robot: Robot) -> int:
        pts = 0
        pts += robot.held_atoms * 1
        pts += robot.scored_atoms * 2
        
        reds = robot.scored_compounds['red'] + robot.held_compounds['red']
        greens = robot.scored_compounds['green'] + robot.held_compounds['green']
        blues = robot.scored_compounds['blue'] + robot.held_compounds['blue']
        total_compounds = reds + greens + blues
        pts += total_compounds * 4
        
        tri_compounds = min(reds, greens, blues)
        pts += tri_compounds * 4
        return pts
