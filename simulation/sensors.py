import math
import numpy as np
from simulation.core import ArenaCore, ROBOT_SIZE, ARENA_SIZE

class Sensors:
    def __init__(self, core: ArenaCore):
        self.core = core
        self.sonar_max_range = 2000.0 # 2 meters
        self.camera_fov = math.radians(150) # 150-degree FOV on the front face
        self.camera_max_range = 1500.0 # 1.5 meters
        
        # Egocentric spatial memory tracking ball locations seen by each robot
        # Mapping: robot_id -> dict of {element_id: (x, y, type, last_seen_time)}
        self.memory = {i: {} for i in range(4)}
        self.postulated_held = {i: 0 for i in range(4)}

    def reset(self):
        """Clears spatial memory and postulated container counts on match reset."""
        self.memory = {i: {} for i in range(4)}
        self.postulated_held = {i: 0 for i in range(4)}

    def _is_line_of_sight_blocked(self, start_x: float, start_y: float, target_x: float, target_y: float, ignore_robot_id: int) -> bool:
        """
        Checks if another robot physically occludes the line of sight between start and target.
        Approximates robots as circular obstacles of radius ROBOT_SIZE / 2.
        """
        vx = target_x - start_x
        vy = target_y - start_y
        dist_sq = vx * vx + vy * vy
        if dist_sq < 1e-4:
            return False
            
        robot_radius = ROBOT_SIZE / 2.0
        for r in self.core.robots:
            if r.id == ignore_robot_id:
                continue
            rx = r.x - start_x
            ry = r.y - start_y
            t = (rx * vx + ry * vy) / dist_sq
            if 0.05 < t < 0.95:
                proj_x = start_x + t * vx
                proj_y = start_y + t * vy
                d_sq = (r.x - proj_x)**2 + (r.y - proj_y)**2
                if d_sq < (robot_radius + 25.0)**2:
                    return True
        return False

    def _raycast_sonar(self, start_x, start_y, angle, max_range, ignore_robot_id):
        """
        Cast a ray for sonars. Detects only arena walls and other robots.
        Sonars do not reliably pick up tiny 20mm/30mm balls on the floor.
        """
        closest_dist = max_range
        
        # 1. Check walls
        if math.cos(angle) < -1e-6:
            dist = -start_x / math.cos(angle)
            if 0 < dist < closest_dist: closest_dist = dist
        if math.cos(angle) > 1e-6:
            dist = (ARENA_SIZE - start_x) / math.cos(angle)
            if 0 < dist < closest_dist: closest_dist = dist
        if math.sin(angle) < -1e-6:
            dist = -start_y / math.sin(angle)
            if 0 < dist < closest_dist: closest_dist = dist
        if math.sin(angle) > 1e-6:
            dist = (ARENA_SIZE - start_y) / math.sin(angle)
            if 0 < dist < closest_dist: closest_dist = dist

        # 2. Check other robots
        for r in self.core.robots:
            if r.id == ignore_robot_id: continue
            
            dx = r.x - start_x
            dy = r.y - start_y
            t = dx * math.cos(angle) + dy * math.sin(angle)
            
            if t > 0:
                closest_x = start_x + t * math.cos(angle)
                closest_y = start_y + t * math.sin(angle)
                dist_to_center = math.hypot(r.x - closest_x, r.y - closest_y)
                
                if dist_to_center < ROBOT_SIZE / 2.0:
                    offset = math.sqrt((ROBOT_SIZE / 2.0)**2 - dist_to_center**2)
                    dist = t - offset
                    if 0 < dist < closest_dist:
                        closest_dist = dist
                        
        return closest_dist

    def _raycast_robot(self, start_x: float, start_y: float, angle: float, max_range: float, ignore_robot_id: int) -> float:
        """
        Cast a ray detecting specifically opponent robots (e.g. computer vision recognition).
        Unlike sonars, this ignores arena walls.
        """
        closest_dist = max_range
        for r in self.core.robots:
            if r.id == ignore_robot_id: continue
            
            dx = r.x - start_x
            dy = r.y - start_y
            t = dx * math.cos(angle) + dy * math.sin(angle)
            
            if t > 0:
                closest_x = start_x + t * math.cos(angle)
                closest_y = start_y + t * math.sin(angle)
                dist_to_center = math.hypot(r.x - closest_x, r.y - closest_y)
                
                if dist_to_center < ROBOT_SIZE / 2.0:
                    offset = math.sqrt((ROBOT_SIZE / 2.0)**2 - dist_to_center**2)
                    dist = t - offset
                    if 0 < dist < closest_dist:
                        closest_dist = dist
                        
        return closest_dist

    def get_sonar_readings(self, robot_id: int):
        """
        Returns normalized distances [-1, 1] for Left (+90 deg), Right (-90 deg), and Back (180 deg) sonars.
        Only detects walls and opponent robots for collision avoidance.
        """
        r = self.core.robots[robot_id]
        angles = [r.theta + math.pi / 2.0, r.theta - math.pi / 2.0, r.theta + math.pi]
        readings = []
        
        for ang in angles:
            dist = self._raycast_sonar(r.x, r.y, ang, self.sonar_max_range, robot_id)
            norm_dist = (dist / self.sonar_max_range) * 2.0 - 1.0
            readings.append(norm_dist)
            
        return readings

    def get_camera_readings(self, robot_id: int):
        """
        Simulates front 150-degree FOV camera.
        Only sees targets in the front 150-degree cone where the camera is mounted.
        Cannot see balls beside or behind the robot.
        Returns 5 pairs: [distance, element_type]
        Types: 0=None, 1=Atom, 2=Red, 3=Green, 4=Blue, 5=Robot
        """
        r = self.core.robots[robot_id]
        angles = np.linspace(-self.camera_fov / 2.0, self.camera_fov / 2.0, 5)
        
        readings = []
        for ang_offset in angles:
            ang = r.theta + ang_offset
            
            closest_dist = self.camera_max_range
            closest_type = 0.0 # None
            
            # Check game elements strictly in front FOV
            for el in self.core.elements:
                if el.scored or el.trapped_by_robot_id is not None: continue
                
                dx = el.x - r.x
                dy = el.y - r.y
                t = dx * math.cos(ang) + dy * math.sin(ang)
                
                if t > 0:
                    closest_x = r.x + t * math.cos(ang)
                    closest_y = r.y + t * math.sin(ang)
                    dist_to_center = math.hypot(el.x - closest_x, el.y - closest_y)
                    
                    if dist_to_center < el.radius:
                        offset = math.sqrt(el.radius**2 - dist_to_center**2)
                        dist = t - offset
                        if 0 < dist < closest_dist:
                            closest_dist = dist
                            if el.type == 'atom': closest_type = 0.2
                            elif el.type == 'red_compound': closest_type = 0.4
                            elif el.type == 'green_compound': closest_type = 0.6
                            elif el.type == 'blue_compound': closest_type = 0.8
                            
            # Check other robots strictly (ignoring walls)
            robot_dist = self._raycast_robot(r.x, r.y, ang, self.camera_max_range, robot_id)
            if robot_dist < closest_dist:
                closest_dist = robot_dist
                closest_type = 1.0 # Robot
                
            norm_dist = (closest_dist / self.camera_max_range) * 2.0 - 1.0
            readings.extend([norm_dist, closest_type])
            
        return readings

    def update(self, robot_id: int):
        """Public update trigger for robot's onboard spatial memory and depletion postulator."""
        self._update_spatial_memory(robot_id)

    def _update_spatial_memory(self, robot_id: int):
        """
        Realistic Embedded Perception (ZERO God-Eye Oracle):
        1. Front 150-deg Camera Detection:
           - Senses uncaptured elements in arena floor within 1.5m and 150-deg FOV cone.
           - Checks line-of-sight occlusion by opponent robots.
           - Updates belief memory with (x, y, type, timestamp).
        2. Visual Ingestion Tracking (Self):
           - When this robot captures a ball through its intake mouth, removes it from
             onboard belief and increments postulated_held.
           - When docked for deposit sequence, resets postulated_held to 0.
        3. Ball Depletion Postulation (Opponent Collection / Displacement):
           - For all remembered balls in belief memory:
             If the robot is looking directly at that location (in 150-deg FOV, < 1.35m,
             unobstructed line-of-sight by other robots), but no ball is detected there,
             the robot postules that an opponent collected it or it was knocked away!
             Removes the missing ball from belief memory.
        4. Stale Memory Decay:
           - Removes remembered balls that have not been re-verified for > 45.0 seconds.
        """
        r = self.core.robots[robot_id]
        current_time = r.active_collection_time

        # 1. Docking deposit and penalty reset
        if r.is_depositing or r.is_penalized:
            self.postulated_held[robot_id] = 0

        # Self-ingestion tracking: remove captured elements near intake and increment held tally
        for el in self.core.elements:
            if el.trapped_by_robot_id == robot_id:
                if el.id in self.memory[robot_id]:
                    del self.memory[robot_id][el.id]
                    self.postulated_held[robot_id] = min(6, self.postulated_held[robot_id] + 1)

        # 2. Live camera detection of free arena elements (with line-of-sight occlusion)
        visible_elements = set()
        for el in self.core.elements:
            # Cannot see scored balls or balls enclosed inside any robot's belly
            if el.scored or el.trapped_by_robot_id is not None:
                continue

            dx = el.x - r.x
            dy = el.y - r.y
            dist = math.hypot(dx, dy)
            if dist <= self.camera_max_range:
                ang = math.atan2(dy, dx)
                rel_ang = (ang - r.theta + math.pi) % (2.0 * math.pi) - math.pi
                if abs(rel_ang) <= self.camera_fov / 2.0:
                    # Line of sight check: if an opponent robot is blocking view, cannot see ball
                    if not self._is_line_of_sight_blocked(r.x, r.y, el.x, el.y, robot_id):
                        visible_elements.add(el.id)
                        prev_entry = self.memory[robot_id].get(el.id, None)
                        if prev_entry is not None and len(prev_entry) >= 4 and (current_time - prev_entry[3]) > 1e-4:
                            dt = current_time - prev_entry[3]
                            el_vx = (el.x - prev_entry[0]) / dt
                            el_vy = (el.y - prev_entry[1]) / dt
                        else:
                            el_vx = getattr(el, 'vx', 0.0)
                            el_vy = getattr(el, 'vy', 0.0)
                        self.memory[robot_id][el.id] = (el.x, el.y, el.type, current_time, el_vx, el_vy)

        # 3. Ball Depletion Postulation (Inferring missing balls from visual evidence)
        elements_to_forget = []
        for el_id, entry in self.memory[robot_id].items():
            if el_id in visible_elements:
                continue

            mem_x, mem_y = entry[0], entry[1]
            last_seen = entry[3] if len(entry) > 3 else current_time
            dx = mem_x - r.x
            dy = mem_y - r.y
            dist = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            rel_ang = (ang - r.theta + math.pi) % (2.0 * math.pi) - math.pi

            # Check if this remembered location is directly within front camera sightline
            in_view_cone = (dist <= self.camera_max_range - 100.0) and (abs(rel_ang) <= (self.camera_fov / 2.0 - math.radians(5)))
            if in_view_cone:
                # If camera is looking straight at the spot without robot occlusion,
                # but no ball is detected there: POSTULATE DEPLETION!
                if not self._is_line_of_sight_blocked(r.x, r.y, mem_x, mem_y, robot_id):
                    elements_to_forget.append(el_id)
            elif (current_time - last_seen) > 45.0:
                # Memory decay over time
                elements_to_forget.append(el_id)

        for el_id in elements_to_forget:
            if el_id in self.memory[robot_id]:
                del self.memory[robot_id][el_id]

    def get_spatial_memory_radar(self, robot_id: int):
        """
        Extracts 8-sector egocentric belief radar from spatial memory (45-degree slices):
        0: Front [-22.5, +22.5 deg]
        1: Front-Left [+22.5, +67.5 deg]
        2: Left [+67.5, +112.5 deg]
        3: Back-Left [+112.5, +157.5 deg]
        4: Rear [157.5, -157.5 deg]
        5: Back-Right [-157.5, -112.5 deg]
        6: Right [-112.5, -67.5 deg]
        7: Front-Right [-67.5, -22.5 deg]
        
        For each sector: [min_norm_distance, ball_density] = 16 continuous features.
        Enables direct Mecanum lateral strafe (Vy) into lines of balls beside the robot.
        """
        r = self.core.robots[robot_id]
        self._update_spatial_memory(robot_id)
        
        sector_min_dist = [2000.0] * 8
        sector_counts = [0] * 8
        sector_width = math.pi / 4.0 # 45 degrees
        
        for el_id, entry in self.memory[robot_id].items():
            mem_x, mem_y = entry[0], entry[1]
            dx = mem_x - r.x
            dy = mem_y - r.y
            dist = math.hypot(dx, dy)
            if dist > 2000.0 or dist < 1.0:
                continue
                
            ang = math.atan2(dy, dx)
            rel_ang = (ang - r.theta + math.pi) % (2.0 * math.pi) - math.pi
            
            # Map rel_ang to sector 0..7
            shifted = (rel_ang + sector_width / 2.0) % (2.0 * math.pi)
            sec_idx = int(shifted / sector_width) % 8
            
            sector_counts[sec_idx] += 1
            if dist < sector_min_dist[sec_idx]:
                sector_min_dist[sec_idx] = dist
                
        radar_features = []
        for s in range(8):
            norm_dist = (sector_min_dist[s] / 2000.0) * 2.0 - 1.0
            norm_density = min(1.0, sector_counts[s] / 4.0)
            radar_features.extend([norm_dist, norm_density])
            
        return radar_features

    def get_net_vector(self, robot_id: int):
        """Relative vector to assigned wall scoring net in local robot coordinates (2 features)."""
        r = self.core.robots[robot_id]
        half = ARENA_SIZE / 2.0
        if r.color == 'yellow': net_x, net_y = half, ARENA_SIZE - 50.0
        elif r.color == 'purple': net_x, net_y = half, 50.0
        elif r.color == 'orange': net_x, net_y = ARENA_SIZE - 50.0, half
        elif r.color == 'green': net_x, net_y = 50.0, half
        else: net_x, net_y = half, half
        
        dx = net_x - r.x
        dy = net_y - r.y
        cos_t = math.cos(r.theta)
        sin_t = math.sin(r.theta)
        local_nx = (dx * cos_t + dy * sin_t) / ARENA_SIZE
        local_ny = (-dx * sin_t + dy * cos_t) / ARENA_SIZE
        return [float(np.clip(local_nx, -1.0, 1.0)), float(np.clip(local_ny, -1.0, 1.0))]

    def get_observation(self, robot_id: int):
        """
        Full 32-dimensional observation vector:
        - 3 Sonar distances (Left, Right, Rear)
        - 10 Camera FOV live rays (5 rays x [dist, type])
        - 16 Egocentric Spatial Memory Radar (8 sectors x [min_dist, density])
        - 2 Local net direction vector [norm_dx, norm_dy]
        - 1 Internal foraging time estimator
        """
        sonars = self.get_sonar_readings(robot_id)
        camera = self.get_camera_readings(robot_id)
        radar = self.get_spatial_memory_radar(robot_id)
        net_vec = self.get_net_vector(robot_id)
        r = self.core.robots[robot_id]
        forage_norm = float(np.clip(r.active_collection_time / 25.0, 0.0, 1.0) * 2.0 - 1.0)
        
        return np.array(sonars + camera + radar + net_vec + [forage_norm], dtype=np.float32)
