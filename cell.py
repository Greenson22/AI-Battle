# cell.py

import pygame
import random
import math
import numpy as np
from settings import *
from neural_network import NeuralNetwork

class Cell:
    def __init__(self, brain: NeuralNetwork = None):
        self.x: float = random.randint(0, LEBAR_LAYAR)
        self.y: float = random.randint(0, TINGGI_LAYAR)
        self.energy: float = ENERGI_AWAL
        self.angle: float = random.uniform(0, 2 * math.pi)
        
        self.fitness: int = 0
        self.current_speed: float = 0
        
        self.brain: NeuralNetwork = brain or NeuralNetwork(NUM_INPUTS, NUM_HIDDEN, NUM_OUTPUTS)
        
        self.leg_animation_cycle = random.uniform(0, 360)
        self.leg_length = RADIUS_SEL * 1.5
        self.leg_swing_arc = math.pi / 4
        self.outline_color = (10, 10, 10)

    def update(self, grass_patches: list, biome: str) -> str:
        """Memperbarui status sel, kini mencari rumput."""
        inputs = self._get_brain_inputs(grass_patches) # Diubah ke rumput
        outputs = self.brain.predict(np.array(inputs))
        self._process_brain_outputs(outputs, biome)
        self._move()
        self._update_status(biome)
        self._update_legs()
        return "hidup" if self.is_alive() else "mati"

    def draw(self, screen: pygame.Surface):
        self._draw_legs(screen)
        self._draw_body(screen)
        self._draw_direction_indicator(screen)
        self._draw_energy_bar(screen)

    def is_alive(self) -> bool:
        return self.energy > 0
        
    def _move(self):
        self.x += self.current_speed * math.cos(self.angle)
        self.y += self.current_speed * math.sin(self.angle)
        self.x = max(0, min(LEBAR_LAYAR, self.x))
        self.y = max(0, min(TINGGI_LAYAR, self.y))

    def _update_legs(self):
        animation_speed = self.current_speed * 2.5
        self.leg_animation_cycle = (self.leg_animation_cycle + animation_speed) % 360
    
    def _draw_legs(self, screen: pygame.Surface):
        leg_color = (40, 40, 40)
        leg_width = 3
        current_swing = math.sin(math.radians(self.leg_animation_cycle)) * self.leg_swing_arc
        
        angle1 = self.angle + math.pi / 2 + current_swing
        end_x1 = self.x + self.leg_length * math.cos(angle1)
        end_y1 = self.y + self.leg_length * math.sin(angle1)
        pygame.draw.line(screen, leg_color, (self.x, self.y), (end_x1, end_y1), leg_width)

        angle2 = self.angle - math.pi / 2 - current_swing
        end_x2 = self.x + self.leg_length * math.cos(angle2)
        end_y2 = self.y + self.leg_length * math.sin(angle2)
        pygame.draw.line(screen, leg_color, (self.x, self.y), (end_x2, end_y2), leg_width)

    def _get_brain_inputs(self, grass_patches: list) -> list:
        """Mengumpulkan data dari rumput terdekat."""
        nearest_grass = self._find_nearest_grass(grass_patches) # Diubah ke rumput
        if not nearest_grass:
            return [1.0, 0.0, self.energy / ENERGI_AWAL]
        
        dist_x = nearest_grass.x - self.x
        dist_y = nearest_grass.y - self.y
        distance = math.hypot(dist_x, dist_y)
        angle_to_grass = math.atan2(dist_y, dist_x) # Diubah ke rumput
        
        norm_dist = min(distance, LEBAR_LAYAR) / LEBAR_LAYAR
        angle_diff = (angle_to_grass - self.angle + math.pi) % (2 * math.pi) - math.pi
        norm_angle = angle_diff / math.pi
        norm_energy = self.energy / ENERGI_AWAL
        return [norm_dist, norm_angle, norm_energy]

    def _find_nearest_grass(self, grass_patches: list):
        """Mencari rumput terdekat."""
        if not grass_patches: return None
        return min(grass_patches, key=lambda g: math.hypot(g.x - self.x, g.y - self.y))

    def _process_brain_outputs(self, outputs: np.ndarray, terrain_type: str):
        turn_left, turn_right, speed_control = outputs
        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        turn_strength = (turn_right - turn_left) * TURN_STRENGTH
        self.angle += turn_strength
        max_speed_on_terrain = KECEPATAN_MAKS_SEL * terrain_modifier['speed_multiplier']
        self.current_speed = (speed_control + 1) / 2 * max_speed_on_terrain

    def _update_status(self, terrain_type: str):
        if terrain_type == 'air':
            self.energy -= ENERGI_TENGGELAM
            self.fitness -= 2
        else:
            terrain_modifier = PENGARUH_TERRAIN[terrain_type]
            speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0
            base_energy_cost = ENERGI_DIAM + (speed_ratio * ENERGI_BERGERAK)
            total_energy_cost = base_energy_cost * terrain_modifier['energy_cost']
            self.energy -= total_energy_cost
        self.fitness += 1
        
    def _draw_body(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.outline_color, (int(self.x), int(self.y)), RADIUS_SEL + 1)
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0
        r = int(WARNA_SEL[0] + (255 - WARNA_SEL[0]) * speed_ratio)
        g = int(WARNA_SEL[1] + (220 - WARNA_SEL[1]) * speed_ratio)
        b = int(WARNA_SEL[2] + (0 - WARNA_SEL[2]) * speed_ratio)
        current_color = (np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255))
        pygame.draw.circle(screen, current_color, (int(self.x), int(self.y)), RADIUS_SEL)

    def _draw_direction_indicator(self, screen: pygame.Surface):
        end_x = self.x + (RADIUS_SEL + 2) * math.cos(self.angle)
        end_y = self.y + (RADIUS_SEL + 2) * math.sin(self.angle)
        pygame.draw.line(screen, (255, 50, 50), (self.x, self.y), (end_x, end_y), 2)

    def _draw_energy_bar(self, screen: pygame.Surface):
        if not self.is_alive(): return
        energy_ratio = self.energy / ENERGI_AWAL
        bar_width = RADIUS_SEL * 2
        bar_height = 4
        bar_x = self.x - RADIUS_SEL
        bar_y = self.y - RADIUS_SEL - 8
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=1)
        r = int(255 * (1 - energy_ratio))
        g = int(255 * energy_ratio)
        energy_color = (np.clip(r, 0, 255), np.clip(g, 0, 255), 0)
        fill_width = bar_width * energy_ratio
        if fill_width > 0:
            pygame.draw.rect(screen, energy_color, (bar_x, bar_y, fill_width, bar_height), border_radius=1)