import pygame
import math
from simulation.core import ArenaCore, ARENA_SIZE, ROBOT_SIZE, ROBOT_HALF, INTAKE_HALF_WIDTH, ATOM_RADIUS, COMPOUND_RADIUS

class Visualizer:
    def __init__(self, core: ArenaCore):
        pygame.init()
        # Scale down the arena for display (2500x2500 -> 750x750 screen)
        self.scale = 0.3
        self.window_size = int(ARENA_SIZE * self.scale)
        self.screen = pygame.display.set_mode((self.window_size, self.window_size))
        pygame.display.set_caption("Unibots 2026 Simulation - The Laboratory")
        self.core = core
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14, bold=True)

    def _transform(self, x, y):
        # Transform from Simulation coordinates (0,0 bottom-left) to Pygame coordinates (0,0 top-left)
        px = int(x * self.scale)
        py = int((ARENA_SIZE - y) * self.scale)
        return px, py

    def render(self):
        # Fill background (dark gray arena floor)
        self.screen.fill((50, 50, 50))
        
        # Draw Scoring Nets (760mm x 100mm on outside of walls)
        net_length = int(760 * self.scale)
        net_thickness = int(60 * self.scale)
        center = self.window_size // 2
        
        # Colors: Yellow (top), Orange (right), Purple (bottom), Green (left)
        pygame.draw.rect(self.screen, (220, 220, 0), (center - net_length//2, 0, net_length, net_thickness)) # Yellow Top
        pygame.draw.rect(self.screen, (220, 130, 0), (self.window_size - net_thickness, center - net_length//2, net_thickness, net_length)) # Orange Right
        pygame.draw.rect(self.screen, (150, 40, 180), (center - net_length//2, self.window_size - net_thickness, net_length, net_thickness)) # Purple Bottom
        pygame.draw.rect(self.screen, (30, 180, 50), (0, center - net_length//2, net_thickness, net_length)) # Green Left

        # Draw Arena perimeter boundary
        pygame.draw.rect(self.screen, (20, 20, 20), (0, 0, self.window_size, self.window_size), 3)

        # Helper to draw an element circle
        def draw_element(el):
            px, py = self._transform(el.x, el.y)
            radius = max(2, int(el.radius * self.scale))
            if el.type == 'atom':
                pygame.draw.circle(self.screen, (230, 230, 230), (px, py), radius)
                pygame.draw.circle(self.screen, (80, 80, 80), (px, py), radius, 1)
            elif el.type == 'red_compound':
                pygame.draw.circle(self.screen, (240, 30, 30), (px, py), radius)
            elif el.type == 'green_compound':
                pygame.draw.circle(self.screen, (40, 220, 40), (px, py), radius)
            elif el.type == 'blue_compound':
                pygame.draw.circle(self.screen, (30, 100, 255), (px, py), radius)

        # 1. Draw Free Game Elements on the floor
        for el in self.core.elements:
            if el.scored or el.trapped_by_robot_id is not None: continue
            draw_element(el)

        # 2. Draw Robots (C-Shaped Chassis) & Trapped Elements
        colors = {
            'yellow': (240, 240, 50),
            'orange': (240, 140, 30),
            'purple': (170, 50, 200),
            'green': (40, 200, 60)
        }
        
        for r in self.core.robots:
            cos_t = math.cos(r.theta)
            sin_t = math.sin(r.theta)
            
            # C-shaped polygon in global space
            c_corners = r.get_c_shape_corners()
            poly_pts = [self._transform(gx, gy) for gx, gy in c_corners]
            
            # Draw C-shaped chassis
            pygame.draw.polygon(self.screen, colors[r.color], poly_pts)
            pygame.draw.polygon(self.screen, (255, 255, 255), poly_pts, 2)

            # Draw Front Intake Opening (150mm gap on front edge)
            left_intake_x = r.x + ROBOT_HALF * cos_t - (-INTAKE_HALF_WIDTH) * sin_t
            left_intake_y = r.y + ROBOT_HALF * sin_t + (-INTAKE_HALF_WIDTH) * cos_t
            right_intake_x = r.x + ROBOT_HALF * cos_t - (INTAKE_HALF_WIDTH) * sin_t
            right_intake_y = r.y + ROBOT_HALF * sin_t + (INTAKE_HALF_WIDTH) * cos_t
            
            p_in_left = self._transform(left_intake_x, left_intake_y)
            p_in_right = self._transform(right_intake_x, right_intake_y)
            
            # Highlight intake opening aperture in dashed/cyan
            pygame.draw.line(self.screen, (0, 255, 255), p_in_left, p_in_right, 2)

            # 3. Draw Elements TRAPPED inside this robot's C-container
            for el in self.core.elements:
                if el.trapped_by_robot_id == r.id and not el.scored:
                    draw_element(el)

            # Camera 150-degree FOV arc rays
            r_center = self._transform(r.x, r.y)
            fov = math.radians(150)
            ray1_x = r.x + 350 * math.cos(r.theta - fov/2)
            ray1_y = r.y + 350 * math.sin(r.theta - fov/2)
            ray2_x = r.x + 350 * math.cos(r.theta + fov/2)
            ray2_y = r.y + 350 * math.sin(r.theta + fov/2)
            
            pygame.draw.line(self.screen, (80, 160, 255), r_center, self._transform(ray1_x, ray1_y), 1)
            pygame.draw.line(self.screen, (80, 160, 255), r_center, self._transform(ray2_x, ray2_y), 1)

            # Draw Sonar Ray indicators (Left, Right, Back)
            s_left = self._transform(r.x + 120 * math.cos(r.theta + math.pi/2), r.y + 120 * math.sin(r.theta + math.pi/2))
            s_right = self._transform(r.x + 120 * math.cos(r.theta - math.pi/2), r.y + 120 * math.sin(r.theta - math.pi/2))
            s_back = self._transform(r.x + 120 * math.cos(r.theta + math.pi), r.y + 120 * math.sin(r.theta + math.pi))
            pygame.draw.line(self.screen, (255, 120, 120), r_center, s_left, 1)
            pygame.draw.line(self.screen, (255, 120, 120), r_center, s_right, 1)
            pygame.draw.line(self.screen, (255, 120, 120), r_center, s_back, 1)

            # Score, penalty, and deposit overlay near robot
            pts = self.core.compute_game_points(r)
            if r.is_penalized:
                score_txt = self.font.render(f"FROZEN:{r.penalty_timer:.1f}s", True, (255, 80, 80))
            elif r.is_depositing:
                score_txt = self.font.render(f"DEPOSITING:{r.deposit_timer:.1f}s", True, (80, 220, 255))
            else:
                score_txt = self.font.render(f"{r.color[:1].upper()}:{pts}p ({r.total_held_elements}/6)", True, (255, 255, 255))
            self.screen.blit(score_txt, (r_center[0] - 30, r_center[1] - 10))

        # Live Leaderboard and Mode Banner in upper-left corner
        panel_y = 10
        if mode_title:
            title_surf = self.font.render(f"MODE: {mode_title} (Press 'M' to switch)", True, (100, 240, 255))
            self.screen.blit(title_surf, (15, panel_y))
            panel_y += 20

        # Team scores for 2v2 mode
        if controller_tags and controller_tags == ['APF', 'APF', 'RL', 'RL']:
            apf_pts = self.core.compute_game_points(self.core.robots[0]) + self.core.compute_game_points(self.core.robots[1])
            rl_pts = self.core.compute_game_points(self.core.robots[2]) + self.core.compute_game_points(self.core.robots[3])
            team_surf = self.font.render(f">> TEAM APF: {apf_pts} pts   VS   TEAM RL: {rl_pts} pts <<", True, (255, 220, 80))
            self.screen.blit(team_surf, (15, panel_y))
            panel_y += 20

        for idx, r in enumerate(self.core.robots):
            pts = self.core.compute_game_points(r)
            tag = f"[{controller_tags[idx]}]" if controller_tags and idx < len(controller_tags) else ""
            if r.is_penalized:
                status_tag = f"[FROZEN: {r.penalty_timer:.1f}s]"
            elif r.is_depositing:
                status_tag = f"[DEPOSITING: {r.deposit_timer:.1f}s]"
            else:
                status_tag = "[ACTIVE]"
            info_str = f"Robot {r.id} ({r.color.capitalize()}) {tag}: {pts} pts | Held: {r.total_held_elements}/6 | Scored: {r.scored_atoms} | Pens: {r.collision_penalty_count} {status_tag}"
            txt_surf = self.font.render(info_str, True, colors[r.color])
            self.screen.blit(txt_surf, (15, panel_y))
            panel_y += 18

        pygame.display.flip()

    def tick(self, fps=30):
        self.clock.tick(fps)
