# cell.py

import pygame
import random
import math
import numpy as np
from settings import *

class NeuralNetwork:
    """Jaringan Saraf Tiruan sederhana sebagai 'otak' sel."""
    def __init__(self, num_inputs, num_hidden, num_outputs):
        self.weights_ih = np.random.uniform(-1, 1, (num_hidden, num_inputs))
        self.weights_ho = np.random.uniform(-1, 1, (num_outputs, num_hidden))

    def predict(self, inputs):
        """Melakukan forward propagation untuk mendapatkan output."""
        hidden = np.dot(self.weights_ih, inputs)
        hidden = np.tanh(hidden)  # Fungsi aktivasi tanh
        outputs = np.dot(self.weights_ho, hidden)
        outputs = np.tanh(outputs)
        return outputs

    @staticmethod
    def crossover(parent1_brain, parent2_brain):
        """Menggabungkan dua 'otak' untuk menciptakan keturunan."""
        child_brain = NeuralNetwork(NUM_INPUTS, NUM_HIDDEN, NUM_OUTPUTS)
        # Crossover weights input-hidden
        midpoint = random.randint(0, child_brain.weights_ih.size)
        child_brain.weights_ih.flat[:midpoint] = parent1_brain.weights_ih.flat[:midpoint]
        child_brain.weights_ih.flat[midpoint:] = parent2_brain.weights_ih.flat[midpoint:]
        # Crossover weights hidden-output
        midpoint = random.randint(0, child_brain.weights_ho.size)
        child_brain.weights_ho.flat[:midpoint] = parent1_brain.weights_ho.flat[:midpoint]
        child_brain.weights_ho.flat[midpoint:] = parent2_brain.weights_ho.flat[midpoint:]
        return child_brain

    def mutate(self, rate, strength):
        """Mengubah bobot secara acak."""
        for i in range(self.weights_ih.shape[0]):
            for j in range(self.weights_ih.shape[1]):
                if random.random() < rate:
                    self.weights_ih[i, j] += random.uniform(-strength, strength)
        for i in range(self.weights_ho.shape[0]):
            for j in range(self.weights_ho.shape[1]):
                if random.random() < rate:
                    self.weights_ho[i, j] += random.uniform(-strength, strength)

class Cell:
    """Sel AI yang dikendalikan oleh Neural Network."""
    def __init__(self, brain=None):
        self.x = random.randint(0, LEBAR_LAYAR)
        self.y = random.randint(0, TINGGI_LAYAR)
        self.energy = ENERGI_AWAL
        self.angle = random.uniform(0, 2 * math.pi)
        self.fitness = 0

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
            
            # Normalisasi input antara -1 dan 1
            norm_dist = min(dist, LEBAR_LAYAR) / LEBAR_LAYAR
            
            angle_to_crystal = math.atan2(dist_y, dist_x)
            angle_diff = (angle_to_crystal - self.angle + math.pi) % (2 * math.pi) - math.pi
            norm_angle = angle_diff / math.pi
            
            inputs = [norm_dist, norm_angle, self.energy / ENERGI_AWAL]
        else:
            inputs = [1.0, 0.0, self.energy / ENERGI_AWAL]

        # 2. Dapatkan keputusan dari 'otak'
        outputs = self.brain.predict(np.array(inputs))
        turn_left, turn_right = outputs[0], outputs[1]
        
        # 3. Lakukan aksi berdasarkan output
        turn_strength = (turn_right - turn_left) * 0.1 # sesuaikan kekuatan belok
        self.angle += turn_strength
        
        self.x += KECEPATAN_SEL * math.cos(self.angle)
        self.y += KECEPATAN_SEL * math.sin(self.angle)
        
        # Batasi pergerakan di dalam layar
        self.x = max(0, min(LEBAR_LAYAR, self.x))
        self.y = max(0, min(TINGGI_LAYAR, self.y))

        # Kurangi energi dan update fitness
        self.energy -= ENERGI_PER_FRAME
        self.fitness += 1
        
        return "hidup" if self.energy > 0 else "mati"

    def draw(self, screen):
        """Menggambar sel dan arahnya."""
        pygame.draw.circle(screen, WARNA_SEL, (int(self.x), int(self.y)), RADIUS_SEL)
        # Gambar garis yang menunjukkan arah
        end_x = self.x + RADIUS_SEL * math.cos(self.angle)
        end_y = self.y + RADIUS_SEL * math.sin(self.angle)
        pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (end_x, end_y), 2)