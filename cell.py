# cell.py

import pygame
import random
import math
import numpy as np
from collections import deque
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
        
        # vvv [BARU] Atribut untuk Kaki vvv
        self.leg_animation_cycle = random.uniform(0, 360) # Titik awal animasi acak
        self.leg_length = RADIUS_SEL * 1.5 # Panjang kaki
        self.leg_swing_arc = math.pi / 4 # Seberapa jauh kaki berayun (45 derajat)
        # ^^^ [BARU] Atribut untuk Kaki ^^^

    def update(self, crystals: list, biome: str) -> str:
        """Memperbarui status sel dan animasi kaki."""
        inputs = self._get_brain_inputs(crystals)
        outputs = self.brain.predict(np.array(inputs))
        self._process_brain_outputs(outputs, biome)
        self._move()
        self._update_status(biome)
        self._update_legs() # <-- Panggil pembaruan animasi kaki
        return "hidup" if self.is_alive() else "mati"

    def draw(self, screen: pygame.Surface):
        """Menggambar sel, dimulai dari kaki."""
        # Urutan gambar: kaki dulu, baru tubuh di atasnya.
        self._draw_legs(screen)
        self._draw_body(screen)
        self._draw_direction_indicator(screen)
        self._draw_energy_bar(screen)

    def is_alive(self) -> bool:
        return self.energy > 0
        
    def _move(self):
        """Memperbarui posisi sel."""
        self.x += self.current_speed * math.cos(self.angle)
        self.y += self.current_speed * math.sin(self.angle)
        self.x = max(0, min(LEBAR_LAYAR, self.x))
        self.y = max(0, min(TINGGI_LAYAR, self.y))

    # vvv [BARU] Logika Animasi Kaki vvv
    def _update_legs(self):
        """Memperbarui siklus animasi kaki berdasarkan kecepatan."""
        # Kecepatan animasi kaki tergantung kecepatan gerak sel
        animation_speed = self.current_speed * 2.5
        self.leg_animation_cycle = (self.leg_animation_cycle + animation_speed) % 360
    # ^^^ [BARU] Logika Animasi Kaki ^^^
    
    # vvv [BARU] Menggambar Kaki vvv
    def _draw_legs(self, screen: pygame.Surface):
        """Menggambar dua kaki yang berayun."""
        leg_color = (40, 40, 40)
        leg_width = 3 # Ketebalan kaki

        # Menghitung ayunan saat ini menggunakan sinus untuk gerakan bolak-balik
        current_swing = math.sin(math.radians(self.leg_animation_cycle)) * self.leg_swing_arc

        # Kaki Kanan
        angle1 = self.angle + math.pi / 2 + current_swing # Arah dasar ke kanan + ayunan
        end_x1 = self.x + self.leg_length * math.cos(angle1)
        end_y1 = self.y + self.leg_length * math.sin(angle1)
        pygame.draw.line(screen, leg_color, (self.x, self.y), (end_x1, end_y1), leg_width)

        # Kaki Kiri
        angle2 = self.angle - math.pi / 2 - current_swing # Arah dasar ke kiri + ayunan berlawanan
        end_x2 = self.x + self.leg_length * math.cos(angle2)
        end_y2 = self.y + self.leg_length * math.sin(angle2)
        pygame.draw.line(screen, leg_color, (self.x, self.y), (end_x2, end_y2), leg_width)
    # ^^^ [BARU] Menggambar Kaki ^^^

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
        if not crystals: return None
        return min(crystals, key=lambda c: math.hypot(c.x - self.x, c.y - self.y))

    def _process_brain_outputs(self, outputs: np.ndarray, terrain_type: str):
        turn_left, turn_right, speed_control = outputs
        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        turn_strength = (turn_right - turn_left) * TURN_STRENGTH
        self.angle += turn_strength
        max_speed_on_terrain = KECEPATAN_MAKS_SEL * terrain_modifier['speed_multiplier']
        self.current_speed = (speed_control + 1) / 2 * max_speed_on_terrain

    def _update_status(self, terrain_type: str):
        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0
        base_energy_cost = ENERGI_DIAM + (speed_ratio * ENERGI_BERGERAK)
        total_energy_cost = base_energy_cost * terrain_modifier['energy_cost']
        self.energy -= total_energy_cost
        self.fitness += 1
        
    def _draw_body(self, screen: pygame.Surface):
        pygame.draw.circle(screen, (10, 10, 10), (int(self.x), int(self.y)), RADIUS_SEL + 1)
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