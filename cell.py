# cell.py

import pygame
import random
import math
import numpy as np
from settings import *
from neural_network import NeuralNetwork
# Tidak perlu import Terrain lagi di sini

class Cell:
    # ... (metode __init__ tidak berubah) ...
    def __init__(self, brain: NeuralNetwork = None):
        self.x: float = random.randint(0, LEBAR_LAYAR)
        self.y: float = random.randint(0, TINGGI_LAYAR)
        self.energy: float = ENERGI_AWAL
        self.angle: float = random.uniform(0, 2 * math.pi)
        
        self.fitness: int = 0
        self.current_speed: float = 0
        
        self.brain: NeuralNetwork = brain or NeuralNetwork(NUM_INPUTS, NUM_HIDDEN, NUM_OUTPUTS)

    # vvv FUNGSI DIPERBAIKI vvv
    def update(self, crystals: list, biome: str) -> str:
        """Memperbarui status sel. Kini menerima string biome."""
        # 1. Ambil informasi dari lingkungan
        inputs = self._get_brain_inputs(crystals)
        
        # 2. Biarkan otak membuat keputusan
        outputs = self.brain.predict(np.array(inputs))
        
        # 3. Lakukan aksi berdasarkan keputusan otak & biome
        self._process_brain_outputs(outputs, biome)
        self._move()
        self._update_status(biome)
        
        return "hidup" if self.is_alive() else "mati"
    # ^^^ FUNGSI DIPERBAIKI ^^^

    # ... (Sisa kode di cell.py tidak ada yang berubah,
    # karena metode _process_brain_outputs dan _update_status
    # memang sudah menerima string biome) ...

    def draw(self, screen: pygame.Surface):
        self._draw_body(screen)
        self._draw_direction_indicator(screen)
        self._draw_energy_bar(screen)

    def is_alive(self) -> bool:
        return self.energy > 0

    def _get_brain_inputs(self, crystals: list) -> list:
        nearest_crystal = self._find_nearest_crystal(crystals)
        if not nearest_crystal:
            return [1.0, 0.0, self.energy / ENERGI_AWAL]
        dist_x = nearest_crystal.x - self.x
        dist_y = nearest_crystal.y - self.y
        distance = math.hypot(dist_x, dist_y)
        angle_to_crystal = math.atan2(dist_y, dist_x)
        norm_dist = min(distance, LEBAR_LAYAR) / LEBAR_LAYAR
        angle_diff = (angle_to_crystal - self.angle + math.pi) % (2 * math.pi) - math.pi
        norm_angle = angle_diff / math.pi
        norm_energy = self.energy / ENERGI_AWAL
        return [norm_dist, norm_angle, norm_energy]

    def _find_nearest_crystal(self, crystals: list):
        if not crystals:
            return None
        return min(crystals, key=lambda c: math.hypot(c.x - self.x, c.y - self.y))

    def _process_brain_outputs(self, outputs: np.ndarray, terrain_type: str):
        turn_left, turn_right, speed_control = outputs
        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        turn_strength = (turn_right - turn_left) * TURN_STRENGTH
        self.angle += turn_strength
        max_speed_on_terrain = KECEPATAN_MAKS_SEL * terrain_modifier['speed_multiplier']
        self.current_speed = (speed_control + 1) / 2 * max_speed_on_terrain

    def _move(self):
        self.x += self.current_speed * math.cos(self.angle)
        self.y += self.current_speed * math.sin(self.angle)
        self.x = max(0, min(LEBAR_LAYAR, self.x))
        self.y = max(0, min(TINGGI_LAYAR, self.y))

    def _update_status(self, terrain_type: str):
        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0
        base_energy_cost = ENERGI_DIAM + (speed_ratio * ENERGI_BERGERAK)
        total_energy_cost = base_energy_cost * terrain_modifier['energy_cost']
        self.energy -= total_energy_cost
        self.fitness += 1

    def _draw_body(self, screen: pygame.Surface):
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0
        r = int(WARNA_SEL[0] + (255 - WARNA_SEL[0]) * speed_ratio)
        g = int(WARNA_SEL[1] + (255 - WARNA_SEL[1]) * speed_ratio)
        b = int(WARNA_SEL[2] + (255 - WARNA_SEL[2]) * speed_ratio)
        current_color = (np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255))
        pygame.draw.circle(screen, current_color, (int(self.x), int(self.y)), RADIUS_SEL)

    def _draw_direction_indicator(self, screen: pygame.Surface):
        end_x = self.x + RADIUS_SEL * math.cos(self.angle)
        end_y = self.y + RADIUS_SEL * math.sin(self.angle)
        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (end_x, end_y), 2)

    def _draw_energy_bar(self, screen: pygame.Surface):
        if not self.is_alive():
            return
        energy_ratio = self.energy / ENERGI_AWAL
        bar_width = RADIUS_SEL * 2
        bar_height = 4
        bar_x = self.x - RADIUS_SEL
        bar_y = self.y - RADIUS_SEL - 8
        r = int(255 * (1 - energy_ratio))
        g = int(255 * energy_ratio)
        energy_color = (np.clip(r, 0, 255), np.clip(g, 0, 255), 0)
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, energy_color, (bar_x, bar_y, bar_width * energy_ratio, bar_height))