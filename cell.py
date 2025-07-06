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
        self.gender = random.choice(['male', 'female'])
        
        # --- Perubahan: Tambahkan atribut state ---
        self.state: str = 'wandering' # Keadaan awal: 'idle', 'wandering', 'foraging', 'running'
        
        self.fitness: int = 0
        self.current_speed: float = 0
        self.brain: NeuralNetwork = brain or NeuralNetwork(NUM_INPUTS, NUM_HIDDEN, NUM_OUTPUTS)
        
        self.leg_animation_cycle = random.uniform(0, 360)
        self.leg_length = RADIUS_SEL * 1.5
        self.leg_swing_arc = math.pi / 4

        if self.gender == 'male':
            self.base_color = (60, 180, 255)
            self.outline_color = (10, 50, 100)
        else:
            self.base_color = (255, 105, 180)
            self.outline_color = (100, 20, 60)

    def update(self, grass_patches: list, biome: str) -> str:
        """Memperbarui status sel berdasarkan state."""
        inputs = self._get_brain_inputs(grass_patches)
        outputs = self.brain.predict(np.array(inputs))
        
        # --- Perubahan: Update state sebelum bertindak ---
        self._update_state(grass_patches, outputs)
        
        self._process_brain_outputs(outputs, biome)
        self._move()
        self._update_status(biome)
        self._update_legs()
        return "hidup" if self.is_alive() else "mati"

    # --- Perubahan: Metode baru untuk mengelola state ---
    def _update_state(self, grass_patches: list, outputs: np.ndarray):
        """Menentukan state sel saat ini."""
        _, _, speed_control = outputs
        nearest_grass = self._find_nearest_grass(grass_patches)
        
        if self.energy < ENERGI_AWAL * 0.25:
            self.state = 'idle'
        elif nearest_grass and math.hypot(nearest_grass.x - self.x, nearest_grass.y - self.y) < JARAK_DETEKSI_MAKANAN:
            self.state = 'foraging'
        elif speed_control > 0.75: # Jika otak memutuskan untuk bergerak cepat
             self.state = 'running'
        else:
            self.state = 'wandering'

    def draw(self, screen: pygame.Surface):
        self._draw_legs(screen)
        self._draw_body(screen)
        self._draw_direction_indicator(screen)
        self._draw_energy_bar(screen)
        self._draw_state_text(screen) # Tampilkan teks state

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
        nearest_grass = self._find_nearest_grass(grass_patches)
        if not nearest_grass:
            return [1.0, 0.0, self.energy / ENERGI_AWAL]
        
        dist_x = nearest_grass.x - self.x
        dist_y = nearest_grass.y - self.y
        distance = math.hypot(dist_x, dist_y)
        angle_to_grass = math.atan2(dist_y, dist_x)
        
        norm_dist = min(distance, LEBAR_LAYAR) / LEBAR_LAYAR
        angle_diff = (angle_to_grass - self.angle + math.pi) % (2 * math.pi) - math.pi
        norm_angle = angle_diff / math.pi
        norm_energy = self.energy / ENERGI_AWAL
        return [norm_dist, norm_angle, norm_energy]

    def _find_nearest_grass(self, grass_patches: list):
        if not grass_patches: return None
        return min(grass_patches, key=lambda g: math.hypot(g.x - self.x, g.y - self.y))

    def _process_brain_outputs(self, outputs: np.ndarray, terrain_type: str):
        # --- Perubahan: Logika disesuaikan berdasarkan state ---
        turn_left, turn_right, speed_control = outputs
        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        max_speed_on_terrain = KECEPATAN_MAKS_SEL * terrain_modifier['speed_multiplier']

        if self.state == 'idle':
            self.current_speed = 0
            return # Tidak perlu memproses putaran jika diam
        
        elif self.state == 'wandering':
            # Bergerak acak dengan kecepatan sedang
            turn_strength = (turn_right - turn_left) * TURN_STRENGTH
            self.angle += turn_strength
            self.current_speed = max_speed_on_terrain * 0.4 # Kecepatan wander
            
        elif self.state == 'foraging':
            # Otak sepenuhnya mengontrol gerakan untuk mengejar makanan
            turn_strength = (turn_right - turn_left) * TURN_STRENGTH
            self.angle += turn_strength
            self.current_speed = (speed_control + 1) / 2 * max_speed_on_terrain
            
        elif self.state == 'running':
            # Bergerak cepat, mengabaikan sedikit belokan untuk lurus
            turn_strength = (turn_right - turn_left) * TURN_STRENGTH * 0.5
            self.angle += turn_strength
            self.current_speed = max_speed_on_terrain # Kecepatan penuh

    def _update_status(self, terrain_type: str):
        if terrain_type == 'air':
            self.energy -= ENERGI_TENGGELAM
            self.fitness -= 2
            return

        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0
        base_energy_cost = ENERGI_DIAM + (speed_ratio * ENERGI_BERGERAK)
        
        # --- Perubahan: Konsumsi energi berdasarkan state ---
        state_multiplier = 1.0
        if self.state == 'running':
            state_multiplier = 2.5 # Berlari menguras energi lebih cepat
        elif self.state == 'idle':
            state_multiplier = 0.5 # Diam sangat hemat energi
            
        total_energy_cost = base_energy_cost * terrain_modifier['energy_cost'] * state_multiplier
        self.energy -= total_energy_cost
        self.fitness += 1
        
    def _draw_body(self, screen: pygame.Surface):
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0
        r = int(self.base_color[0] + (255 - self.base_color[0]) * speed_ratio)
        g = int(self.base_color[1] + (220 - self.base_color[1]) * speed_ratio)
        b = int(self.base_color[2] + (0 - self.base_color[2]) * speed_ratio)
        current_color = (np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255))

        if self.gender == 'male':
            rect = pygame.Rect(self.x - RADIUS_SEL * 1.2, self.y - RADIUS_SEL * 0.8, RADIUS_SEL * 2.4, RADIUS_SEL * 1.6)
            pygame.draw.ellipse(screen, self.outline_color, rect.inflate(2, 2))
            pygame.draw.ellipse(screen, current_color, rect)
        else:
            pygame.draw.circle(screen, self.outline_color, (int(self.x), int(self.y)), RADIUS_SEL + 1)
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

# --- Perubahan: Metode untuk menampilkan teks state dengan inisial ---
    def _draw_state_text(self, screen: pygame.Surface):
        """Menampilkan inisial state sel saat ini di atasnya."""
        if not hasattr(self, 'font'):
            # Sedikit perbesar font agar inisial jelas terlihat
            self.font = pygame.font.Font(None, 20) 
        
        # Ambil huruf pertama dari state sebagai inisial
        state_initial = self.state[0].upper()
        
        text_surface = self.font.render(state_initial, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x, self.y - RADIUS_SEL - 18))
        
        # Tambahkan background gelap kecil agar teks lebih mudah dibaca
        bg_rect = text_rect.inflate(4, 4)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect, border_radius=3)

        screen.blit(text_surface, text_rect)