# cell.py

import pygame
import random
import math
import numpy as np
from settings import *
from neural_network import NeuralNetwork
from terrain import Terrain # <- DI TAMBAHKAN

class Cell:
    """
    Mewakili sel AI yang dikendalikan oleh Jaringan Saraf Tiruan.
    Setiap sel memiliki tujuan untuk bertahan hidup dengan mencari energi
    dan berevolusi dari generasi ke generasi.
    """
    def __init__(self, brain: NeuralNetwork = None):
        """Inisialisasi status awal sel."""
        self.x: float = random.randint(0, LEBAR_LAYAR)
        self.y: float = random.randint(0, TINGGI_LAYAR)
        self.energy: float = ENERGI_AWAL
        self.angle: float = random.uniform(0, 2 * math.pi)

        self.fitness: int = 0
        self.current_speed: float = 0

        # Gunakan otak yang diwariskan atau buat yang baru
        self.brain: NeuralNetwork = brain or NeuralNetwork(NUM_INPUTS, NUM_HIDDEN, NUM_OUTPUTS)

    # --- Metode Utama ---
    # vvv DIUBAH vvv
    def update(self, crystals: list, terrain: Terrain) -> str:
        """Memperbarui status sel untuk satu frame."""
        # 1. Ambil informasi dari lingkungan
        inputs = self._get_brain_inputs(crystals)

        # 2. Biarkan otak membuat keputusan
        outputs = self.brain.predict(np.array(inputs))

        # 3. Dapatkan tipe terrain saat ini
        current_terrain = terrain.get_terrain_type_at(self.x, self.y)

        # 4. Lakukan aksi berdasarkan keputusan otak & terrain
        self._process_brain_outputs(outputs, current_terrain)
        self._move()
        self._update_status(current_terrain) # Kirim info terrain

        return "hidup" if self.is_alive() else "mati"
    # ^^^ DIUBAH ^^^

    def draw(self, screen: pygame.Surface):
        """Menggambar sel dan semua indikatornya ke layar."""
        self._draw_body(screen)
        self._draw_direction_indicator(screen)
        self._draw_energy_bar(screen)

    def is_alive(self) -> bool:
        """Memeriksa apakah sel masih memiliki energi."""
        return self.energy > 0

    # --- Metode Privat untuk Logika Internal ---
    def _get_brain_inputs(self, crystals: list) -> list:
        """Mengumpulkan dan menormalisasi data untuk input otak."""
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
        """Mencari kristal terdekat dari posisi sel."""
        if not crystals:
            return None
        return min(crystals, key=lambda c: math.hypot(c.x - self.x, c.y - self.y))

    # vvv DIUBAH vvv
    def _process_brain_outputs(self, outputs: np.ndarray, terrain_type: str):
        """Menerjemahkan output otak menjadi aksi belok dan kecepatan."""
        turn_left, turn_right, speed_control = outputs
        terrain_modifier = PENGARUH_TERRAIN[terrain_type]

        turn_strength = (turn_right - turn_left) * TURN_STRENGTH
        self.angle += turn_strength

        # Kecepatan maks disesuaikan dengan terrain
        max_speed_on_terrain = KECEPATAN_MAKS_SEL * terrain_modifier['speed_multiplier']
        self.current_speed = (speed_control + 1) / 2 * max_speed_on_terrain
    # ^^^ DIUBAH ^^^

    def _move(self):
        """Menggerakkan sel dan memastikan tetap di dalam layar."""
        self.x += self.current_speed * math.cos(self.angle)
        self.y += self.current_speed * math.sin(self.angle)

        self.x = max(0, min(LEBAR_LAYAR, self.x))
        self.y = max(0, min(TINGGI_LAYAR, self.y))

    # vvv DIUBAH vvv
    def _update_status(self, terrain_type: str):
        """Memperbarui energi dan fitness sel."""
        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0

        # Biaya energi dasar dipengaruhi terrain
        base_energy_cost = ENERGI_DIAM + (speed_ratio * ENERGI_BERGERAK)
        total_energy_cost = base_energy_cost * terrain_modifier['energy_cost']

        self.energy -= total_energy_cost
        self.fitness += 1
    # ^^^ DIUBAH ^^^

    # --- Metode Privat untuk Menggambar ---
    def _draw_body(self, screen: pygame.Surface):
        """Menggambar tubuh sel dengan warna yang merepresentasikan kecepatan."""
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0

        r = int(WARNA_SEL[0] + (255 - WARNA_SEL[0]) * speed_ratio)
        g = int(WARNA_SEL[1] + (255 - WARNA_SEL[1]) * speed_ratio)
        b = int(WARNA_SEL[2] + (255 - WARNA_SEL[2]) * speed_ratio)
        current_color = (np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255))

        pygame.draw.circle(screen, current_color, (int(self.x), int(self.y)), RADIUS_SEL)

    def _draw_direction_indicator(self, screen: pygame.Surface):
        """Menggambar garis yang menunjukkan arah hadap sel."""
        end_x = self.x + RADIUS_SEL * math.cos(self.angle)
        end_y = self.y + RADIUS_SEL * math.sin(self.angle)
        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (end_x, end_y), 2)

    def _draw_energy_bar(self, screen: pygame.Surface):
        """Menggambar bilah energi di atas sel."""
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