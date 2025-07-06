import pygame
import random
import math
import numpy as np
from settings import *
from neural_network import NeuralNetwork

class Cell:
    """Sel AI yang dikendalikan oleh Neural Network."""
    def __init__(self, brain=None):
        self.x = random.randint(0, LEBAR_LAYAR)
        self.y = random.randint(0, TINGGI_LAYAR)
        self.energy = ENERGI_AWAL
        self.angle = random.uniform(0, 2 * math.pi)
        self.fitness = 0
        # Tambahkan variabel untuk kecepatan saat ini agar bisa diakses di draw()
        self.current_speed = 0

        if brain:
            self.brain = brain
        else:
            self.brain = NeuralNetwork(NUM_INPUTS, NUM_HIDDEN, NUM_OUTPUTS)

    def find_nearest_crystal(self, crystals):
        """Mencari kristal terdekat."""
        if not crystals: return None
        return min(crystals, key=lambda c: math.hypot(c.x - self.x, c.y - self.y))

    def update(self, crystals):
        """Menggunakan 'otak' untuk memutuskan gerakan."""
        # 1. Kumpulkan Input untuk 'otak'
        nearest_crystal = self.find_nearest_crystal(crystals)
        if nearest_crystal:
            dist_x = nearest_crystal.x - self.x
            dist_y = nearest_crystal.y - self.y
            dist = math.hypot(dist_x, dist_y)
            
            norm_dist = min(dist, LEBAR_LAYAR) / LEBAR_LAYAR
            
            angle_to_crystal = math.atan2(dist_y, dist_x)
            angle_diff = (angle_to_crystal - self.angle + math.pi) % (2 * math.pi) - math.pi
            norm_angle = angle_diff / math.pi
            
            inputs = [norm_dist, norm_angle, self.energy / ENERGI_AWAL]
        else:
            inputs = [1.0, 0.0, self.energy / ENERGI_AWAL]

        # 2. Dapatkan keputusan dari 'otak'
        outputs = self.brain.predict(np.array(inputs))
        turn_left, turn_right, speed_control = outputs[0], outputs[1], outputs[2]
        
        # 3. Lakukan aksi berdasarkan output
        turn_strength = (turn_right - turn_left) * 0.1
        self.angle += turn_strength
        
        # Otak mengontrol kecepatan
        self.current_speed = (speed_control + 1) / 2 * KECEPATAN_MAKS_SEL
        
        self.x += self.current_speed * math.cos(self.angle)
        self.y += self.current_speed * math.sin(self.angle)
        
        # Batasi pergerakan di dalam layar
        self.x = max(0, min(LEBAR_LAYAR, self.x))
        self.y = max(0, min(TINGGI_LAYAR, self.y))

        # Kurangi energi berdasarkan kecepatan
        energy_cost = ENERGI_DIAM + (self.current_speed / KECEPATAN_MAKS_SEL) * ENERGI_BERGERAK
        self.energy -= energy_cost
        self.fitness += 1
        
        return "hidup" if self.energy > 0 else "mati"

    def draw(self, screen):
        """Menggambar sel, arah, dan indikator statusnya."""
        # --- BARU: Indikator Kecepatan (perubahan warna sel) ---
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL
        # Campurkan WARNA_SEL dengan putih berdasarkan kecepatan
        # Semakin cepat, semakin mendekati putih
        r = int(WARNA_SEL[0] + (255 - WARNA_SEL[0]) * speed_ratio)
        g = int(WARNA_SEL[1] + (255 - WARNA_SEL[1]) * speed_ratio)
        b = int(WARNA_SEL[2] + (255 - WARNA_SEL[2]) * speed_ratio)
        current_color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
        
        pygame.draw.circle(screen, current_color, (int(self.x), int(self.y)), RADIUS_SEL)

        # Gambar garis yang menunjukkan arah
        end_x = self.x + RADIUS_SEL * math.cos(self.angle)
        end_y = self.y + RADIUS_SEL * math.sin(self.angle)
        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (end_x, end_y), 2)
        
        # --- BARU: Indikator Energi (bilah di atas sel) ---
        if self.energy > 0:
            energy_ratio = self.energy / ENERGI_AWAL
            bar_width = RADIUS_SEL * 2
            bar_height = 4
            bar_x = self.x - RADIUS_SEL
            bar_y = self.y - RADIUS_SEL - 8 # Posisi di atas sel
            
            # Warna bilah dari hijau ke merah
            energy_color = (max(0, min(255, int(255 * (1 - energy_ratio)))), max(0, min(255, int(255 * energy_ratio))), 0)
            
            # Gambar latar belakang bilah
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            # Gambar bilah energi
            pygame.draw.rect(screen, energy_color, (bar_x, bar_y, bar_width * energy_ratio, bar_height))