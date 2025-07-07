# cell.py
import pygame
import random
import math
import numpy as np
from settings import *
from neural_network import NeuralNetwork
from grass import Grass
from terrain import Terrain

class Cell:
    def __init__(self, brain: NeuralNetwork = None):
        self.x: float = random.randint(0, LEBAR_LAYAR)
        self.y: float = random.randint(0, TINGGI_LAYAR)
        self.energy: float = ENERGI_AWAL
        self.angle: float = random.uniform(0, 2 * math.pi)
        self.gender = random.choice(['male', 'female'])
        
        self.possible_states = ['idle', 'wandering', 'foraging', 'running']
        self.state: str = 'wandering'
        
        self.fitness: int = 0
        self.current_speed: float = 0
        self.brain: NeuralNetwork = brain or NeuralNetwork(NUM_INPUTS, NUM_HIDDEN, NUM_OUTPUTS)
        
        self.leg_animation_cycle = random.uniform(0, 360)
        self.leg_length = RADIUS_SEL * 1.5
        self.leg_swing_arc = math.pi / 4
        
        self.target_grass = None

        if self.gender == 'male':
            self.base_color = (60, 180, 255)
            self.outline_color = (10, 50, 100)
        else:
            self.base_color = (255, 105, 180)
            self.outline_color = (100, 20, 60)
            
    def update(self, grass_patches: list, all_cells: list, terrain: Terrain) -> str:
        self.target_grass = self._find_nearest_grass(grass_patches)
        biome_at_cell = terrain.get_biome_at(self.x, self.y)

        # Mengirim daftar sel lain ke fungsi input untuk dideteksi oleh sensor
        inputs = self._get_brain_inputs(self.target_grass, terrain, all_cells)
        outputs = self.brain.predict(np.array(inputs))
        
        self._update_state_from_brain(outputs)
        self._process_brain_outputs(outputs, biome_at_cell)
        
        self._move()
        self._update_social_fitness(all_cells)
        self._update_status(biome_at_cell)
        self._update_legs()
        
        return "hidup" if self.is_alive() else "mati"
    
    def draw(self, screen: pygame.Surface, show_debug: bool = False, all_cells: list = None):
        self._draw_legs(screen)
        self._draw_body(screen)
        self._draw_direction_indicator(screen)
        self._draw_energy_bar(screen)
        
        if show_debug:
            self._draw_state_text(screen)
            self._draw_foraging_line(screen)
            self._draw_fitness_bar(screen)
            # Mengirim daftar sel untuk visualisasi sensor
            if all_cells:
                self._draw_terrain_sensors(screen, all_cells)

    def _get_brain_inputs(self, nearest_grass: Grass, terrain: Terrain, all_cells: list) -> list:
        # Input dasar (makanan & energi)
        if not nearest_grass:
            norm_dist, norm_angle = 1.0, 0.0
        else:
            dist_x, dist_y = nearest_grass.x - self.x, nearest_grass.y - self.y
            distance = math.hypot(dist_x, dist_y)
            angle_to_grass = math.atan2(dist_y, dist_x)
            norm_dist = min(distance, LEBAR_LAYAR) / LEBAR_LAYAR
            angle_diff = (angle_to_grass - self.angle + math.pi) % (2 * math.pi) - math.pi
            norm_angle = angle_diff / math.pi
        norm_energy = self.energy / ENERGI_AWAL
        base_inputs = [norm_dist, norm_angle, norm_energy]

        # Input dari sensor
        terrain_sensor_inputs = []
        cell_sensor_inputs = [] # List baru untuk sensor sel
        
        for i in range(JUMLAH_SENSOR_TERRAIN):
            sensor_angle = self.angle + (i * (2 * math.pi / JUMLAH_SENSOR_TERRAIN))
            sensor_x = self.x + JARAK_PENGLIHATAN_SEL * math.cos(sensor_angle)
            sensor_y = self.y + JARAK_PENGLIHATAN_SEL * math.sin(sensor_angle)

            # 1. Logika Sensor Terrain
            biome_type = terrain.get_biome_at(sensor_x, sensor_y)
            terrain_sensor_inputs.append(NILAI_SENSOR_TERRAIN.get(biome_type, 0.0))

            # 2. Logika Sensor Sel
            cell_detected = 0.0
            for other_cell in all_cells:
                if other_cell is self:
                    continue
                dist_to_other = math.hypot(sensor_x - other_cell.x, sensor_y - other_cell.y)
                if dist_to_other < RADIUS_SEL:
                    cell_detected = 1.0
                    break 
            cell_sensor_inputs.append(cell_detected)

        # Gabungkan semua input menjadi satu
        return base_inputs + terrain_sensor_inputs + cell_sensor_inputs

    def _process_brain_outputs(self, outputs: np.ndarray, terrain_type: str):
        turn_left, turn_right, speed_control = outputs[:3]
        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        max_speed_on_terrain = KECEPATAN_MAKS_SEL * terrain_modifier['speed_multiplier']

        if self.state == 'idle':
            self.current_speed = 0
        elif self.state == 'wandering':
            self.angle += (turn_right - turn_left) * TURN_STRENGTH
            self.current_speed = max_speed_on_terrain * 0.4
        elif self.state == 'foraging':
            self.angle += (turn_right - turn_left) * TURN_STRENGTH
            self.current_speed = (speed_control + 1) / 2 * max_speed_on_terrain
        elif self.state == 'running':
            self.angle += (turn_right - turn_left) * TURN_STRENGTH * 0.5
            self.current_speed = max_speed_on_terrain
    
    def _update_state_from_brain(self, outputs: np.ndarray):
        state_outputs = outputs[3:]
        chosen_state_index = np.argmax(state_outputs)
        self.state = self.possible_states[chosen_state_index]

    def _find_nearest_grass(self, grass_patches: list):
        if not grass_patches: return None
        return min(grass_patches, key=lambda g: math.hypot(g.x - self.x, g.y - self.y))

    def _move(self):
        self.x += self.current_speed * math.cos(self.angle)
        self.y += self.current_speed * math.sin(self.angle)
        self.x = max(0, min(LEBAR_LAYAR, self.x))
        self.y = max(0, min(TINGGI_LAYAR, self.y))
    
    def _update_status(self, terrain_type: str):
        if terrain_type == 'air':
            self.fitness -= 2
            return
        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0
        base_energy_cost = ENERGI_DIAM + (speed_ratio * ENERGI_BERGERAK)
        state_multiplier = 1.0
        if self.state == 'running': state_multiplier = 2.5
        elif self.state == 'idle':
            state_multiplier = 0.5
            self.fitness -= 0.5
        total_energy_cost = base_energy_cost * terrain_modifier['energy_cost'] * state_multiplier
        self.energy -= total_energy_cost
        self.fitness += 1
    
    def _update_social_fitness(self, all_cells: list):
        nearby_friends = 0
        for other_cell in all_cells:
            if other_cell is self: continue
            if math.hypot(self.x - other_cell.x, self.y - other_cell.y) < JARAK_DETEKSI_SOSIAL:
                nearby_friends += 1
        if nearby_friends >= 5:
            self.fitness += BONUS_FITNESS_SOSIAL
    
    def is_alive(self) -> bool:
        return self.energy > 0

    def _draw_body(self, screen: pygame.Surface):
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0
        r, g, b = self.base_color
        current_color = (
            np.clip(int(r + (255 - r) * speed_ratio), 0, 255),
            np.clip(int(g + (220 - g) * speed_ratio), 0, 255),
            np.clip(int(b + (0 - b) * speed_ratio), 0, 255)
        )
        if self.gender == 'male':
            rect = pygame.Rect(self.x - RADIUS_SEL * 1.2, self.y - RADIUS_SEL * 0.8, RADIUS_SEL * 2.4, RADIUS_SEL * 1.6)
            pygame.draw.ellipse(screen, self.outline_color, rect.inflate(2, 2))
            pygame.draw.ellipse(screen, current_color, rect)
        else:
            pygame.draw.circle(screen, self.outline_color, (int(self.x), int(self.y)), RADIUS_SEL + 1)
            pygame.draw.circle(screen, current_color, (int(self.x), int(self.y)), RADIUS_SEL)
    
    def _draw_legs(self, screen: pygame.Surface):
        current_swing = math.sin(math.radians(self.leg_animation_cycle)) * self.leg_swing_arc
        for sign in [-1, 1]:
            angle = self.angle + (sign * math.pi / 2) - (sign * current_swing)
            end_pos = (self.x + self.leg_length * math.cos(angle), self.y + self.leg_length * math.sin(angle))
            pygame.draw.line(screen, (40, 40, 40), (self.x, self.y), end_pos, 3)
    
    def _update_legs(self):
        self.leg_animation_cycle = (self.leg_animation_cycle + self.current_speed * 2.5) % 360
    
    def _draw_direction_indicator(self, screen: pygame.Surface):
        end_x = self.x + (RADIUS_SEL + 2) * math.cos(self.angle)
        end_y = self.y + (RADIUS_SEL + 2) * math.sin(self.angle)
        pygame.draw.line(screen, (255, 50, 50), (self.x, self.y), (end_x, end_y), 2)

    def _draw_energy_bar(self, screen: pygame.Surface):
        if not self.is_alive(): return
        bar_pos = (self.x - RADIUS_SEL, self.y + RADIUS_SEL + 4)
        bar_size = (RADIUS_SEL * 2, 4)
        energy_ratio = self.energy / ENERGI_AWAL
        fill_width = bar_size[0] * energy_ratio
        r, g = int(255 * (1 - energy_ratio)), int(255 * energy_ratio)
        energy_color = (np.clip(r, 0, 255), np.clip(g, 0, 255), 0)
        pygame.draw.rect(screen, (50, 50, 50), (*bar_pos, *bar_size), border_radius=1)
        if fill_width > 0:
            pygame.draw.rect(screen, energy_color, (*bar_pos, fill_width, bar_size[1]), border_radius=1)
    
    def _draw_fitness_bar(self, screen: pygame.Surface):
        if not self.is_alive(): return
        bar_pos = (self.x - RADIUS_SEL, self.y + RADIUS_SEL + 10)
        bar_size = (RADIUS_SEL * 2, 4)
        fill_width = bar_size[0] * ((self.fitness % 1000) / 1000.0)
        pygame.draw.rect(screen, (50, 50, 50), (*bar_pos, *bar_size), border_radius=1)
        if fill_width > 0:
            pygame.draw.rect(screen, (138, 43, 226), (*bar_pos, fill_width, bar_size[1]), border_radius=1)

    def _draw_state_text(self, screen: pygame.Surface):
        if not hasattr(self, 'font'):
            self.font = pygame.font.Font(None, 20)
        text_surf = self.font.render(self.state[0].upper(), True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.x, self.y - RADIUS_SEL - 18))
        pygame.draw.rect(screen, (0, 0, 0, 128), text_rect.inflate(4, 4), border_radius=3)
        screen.blit(text_surf, text_rect)
    
    def _draw_foraging_line(self, screen: pygame.Surface):
        if self.state == 'foraging' and self.target_grass:
            if math.hypot(self.target_grass.x - self.x, self.target_grass.y - self.y) < JARAK_DETEKSI_MAKANAN:
                pygame.draw.line(screen, (255, 255, 0), (self.x, self.y), (self.target_grass.x, self.target_grass.y), 1)

    def _draw_terrain_sensors(self, screen: pygame.Surface, all_cells: list):
        for i in range(JUMLAH_SENSOR_TERRAIN):
            sensor_angle = self.angle + (i * (2 * math.pi / JUMLAH_SENSOR_TERRAIN))
            sensor_x = self.x + JARAK_PENGLIHATAN_SEL * math.cos(sensor_angle)
            sensor_y = self.y + JARAK_PENGLIHATAN_SEL * math.sin(sensor_angle)
            sensor_color = (255, 255, 255)
            for other_cell in all_cells:
                if other_cell is not self and math.hypot(sensor_x - other_cell.x, sensor_y - other_cell.y) < RADIUS_SEL:
                    sensor_color = (255, 0, 0)
                    break
            pygame.draw.line(screen, (100, 100, 100), (self.x, self.y), (sensor_x, sensor_y), 1)
            pygame.draw.circle(screen, sensor_color, (int(sensor_x), int(sensor_y)), 3)