# cell.py
import pygame
import random
import math
import numpy as np
from settings import *
from neural_network import NeuralNetwork
from grass import Grass

class Cell:
    """
    Mendefinisikan agen individu (sel) dalam simulasi.
    Setiap sel memiliki otak (jaringan saraf), status, energi, dan kemampuan untuk
    berinteraksi dengan lingkungannya.
    """
    def __init__(self, brain: NeuralNetwork = None):
        """
        Menginisialisasi sebuah sel baru.

        Args:
            brain (NeuralNetwork, optional): Otak jaringan saraf yang sudah ada. 
                                            Jika tidak ada, otak baru akan dibuat.
        """
        # --- Atribut Fisik & Posisi ---
        self.x: float = random.randint(0, LEBAR_LAYAR)
        self.y: float = random.randint(0, TINGGI_LAYAR)
        self.angle: float = random.uniform(0, 2 * math.pi)

        # --- Atribut Biologis & Status ---
        self.energy: float = ENERGI_AWAL
        self.gender = random.choice(['male', 'female'])
        self.fitness: int = 0
        
        # --- Status Perilaku ---
        self.possible_states = ['idle', 'wandering', 'foraging', 'running']
        self.state: str = 'wandering'
        
        # --- Otak & Pergerakan ---
        self.current_speed: float = 0
        self.brain: NeuralNetwork = brain or NeuralNetwork(NUM_INPUTS, NUM_HIDDEN, NUM_OUTPUTS)
        self.target_grass = None

        # --- Atribut Visual & Animasi ---
        self.leg_animation_cycle = random.uniform(0, 360)
        self.leg_length = RADIUS_SEL * 1.5
        self.leg_swing_arc = math.pi / 4

        # Atur warna berdasarkan jenis kelamin untuk identifikasi visual
        if self.gender == 'male':
            self.base_color = (60, 180, 255)  # Biru
            self.outline_color = (10, 50, 100)
        else:
            self.base_color = (255, 105, 180) # Pink
            self.outline_color = (100, 20, 60)
            
    def update(self, grass_patches: list, all_cells: list, biome: str) -> str:
        """
        Siklus hidup utama sel, dipanggil setiap frame.
        Mengkoordinasikan persepsi, pengambilan keputusan, dan aksi.

        Args:
            grass_patches (list): Daftar semua objek rumput di simulasi.
            all_cells (list): Daftar semua sel lain di simulasi.
            biome (str): Jenis medan tempat sel saat ini berada.

        Returns:
            str: Status sel ("hidup" atau "mati").
        """
        # 1. Persepsi: Temukan makanan terdekat
        self.target_grass = self._find_nearest_grass(grass_patches)
        
        # 2. Berpikir: Dapatkan input dan buat prediksi dengan otak
        inputs = self._get_brain_inputs(self.target_grass)
        outputs = self.brain.predict(np.array(inputs))
        
        # 3. Aksi: Perbarui status, kecepatan, dan arah berdasarkan output otak
        self._update_state_from_brain(outputs)
        self._process_brain_outputs(outputs, biome)
        
        # 4. Terapkan Aksi & Perbarui Status Internal
        self._move()
        self._update_social_fitness(all_cells) # Cek interaksi sosial
        self._update_status(biome)             # Perbarui energi & fitness
        self._update_legs()                    # Perbarui animasi
        
        return "hidup" if self.is_alive() else "mati"
    
    def draw(self, screen: pygame.Surface, show_debug: bool = False):
        """
        Menggambar sel dan semua elemen visualnya ke layar.

        Args:
            screen (pygame.Surface): Permukaan pygame untuk menggambar.
            show_debug (bool): Jika True, tampilkan informasi debug tambahan.
        """
        self._draw_legs(screen)
        self._draw_body(screen)
        self._draw_direction_indicator(screen)
        self._draw_energy_bar(screen)
        
        if show_debug:
            self._draw_state_text(screen)
            self._draw_foraging_line(screen)
            self._draw_fitness_bar(screen)

    # =======================================================
    # Kecerdasan Buatan & Pengambilan Keputusan 🧠
    # =======================================================
    
    def _get_brain_inputs(self, nearest_grass: Grass) -> list:
        """
        Menyiapkan input untuk jaringan saraf berdasarkan persepsi lingkungan.
        """
        # Jika tidak ada rumput, input menunjukkan tidak ada target
        if not nearest_grass:
            return [1.0, 0.0, self.energy / ENERGI_AWAL]
        
        # Hitung jarak dan sudut ke rumput terdekat
        dist_x = nearest_grass.x - self.x
        dist_y = nearest_grass.y - self.y
        distance = math.hypot(dist_x, dist_y)
        angle_to_grass = math.atan2(dist_y, dist_x)
        
        # Normalisasi nilai agar cocok untuk input jaringan saraf (antara -1 dan 1)
        norm_dist = min(distance, LEBAR_LAYAR) / LEBAR_LAYAR
        angle_diff = (angle_to_grass - self.angle + math.pi) % (2 * math.pi) - math.pi
        norm_angle = angle_diff / math.pi
        norm_energy = self.energy / ENERGI_AWAL
        
        return [norm_dist, norm_angle, norm_energy]
    
    def _process_brain_outputs(self, outputs: np.ndarray, terrain_type: str):
        """Menerjemahkan output dari jaringan saraf menjadi tindakan nyata."""
        turn_left, turn_right, speed_control = outputs[:3]
        
        # Sesuaikan kecepatan maksimum berdasarkan medan
        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        max_speed_on_terrain = KECEPATAN_MAKS_SEL * terrain_modifier['speed_multiplier']

        if self.state == 'idle':
            self.current_speed = 0
            return
        
        # Logika gerakan untuk setiap status
        elif self.state == 'wandering':
            turn_strength = (turn_right - turn_left) * TURN_STRENGTH
            self.angle += turn_strength
            self.current_speed = max_speed_on_terrain * 0.4
            
        elif self.state == 'foraging':
            turn_strength = (turn_right - turn_left) * TURN_STRENGTH
            self.angle += turn_strength
            self.current_speed = (speed_control + 1) / 2 * max_speed_on_terrain
            
        elif self.state == 'running':
            turn_strength = (turn_right - turn_left) * TURN_STRENGTH * 0.5
            self.angle += turn_strength
            self.current_speed = max_speed_on_terrain
    
    def _update_state_from_brain(self, outputs: np.ndarray):
        """Memilih status perilaku berdasarkan output otak."""
        state_outputs = outputs[3:]
        chosen_state_index = np.argmax(state_outputs)
        self.state = self.possible_states[chosen_state_index]

    def _find_nearest_grass(self, grass_patches: list):
        """Menemukan objek rumput terdekat dari sel."""
        if not grass_patches: return None
        return min(grass_patches, key=lambda g: math.hypot(g.x - self.x, g.y - self.y))

    # =======================================================
    # Aksi & Status Internal ⚡
    # =======================================================

    def _move(self):
        """Memperbarui posisi sel berdasarkan kecepatan dan arahnya."""
        self.x += self.current_speed * math.cos(self.angle)
        self.y += self.current_speed * math.sin(self.angle)
        # Mencegah sel keluar dari batas layar
        self.x = max(0, min(LEBAR_LAYAR, self.x))
        self.y = max(0, min(TINGGI_LAYAR, self.y))
    
    def _update_status(self, terrain_type: str):
        """Memperbarui energi dan kebugaran sel setiap frame."""
        # Penalti jika tenggelam di air
        if terrain_type == 'air':
            self.energy -= ENERGI_TENGGELAM
            self.fitness -= 2
            return

        terrain_modifier = PENGARUH_TERRAIN[terrain_type]
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0
        base_energy_cost = ENERGI_DIAM + (speed_ratio * ENERGI_BERGERAK)
        
        # Pengali biaya energi berdasarkan status
        state_multiplier = 1.0
        if self.state == 'running':
            state_multiplier = 2.5
        elif self.state == 'idle':
            state_multiplier = 0.5
            self.fitness -= 0.5 # Penalti kecil karena tidak melakukan apa-apa
            
        # Hitung total biaya energi
        total_energy_cost = base_energy_cost * terrain_modifier['energy_cost'] * state_multiplier
        self.energy -= total_energy_cost
        self.fitness += 1 # Fitness dasar untuk bertahan hidup
    
    def _update_social_fitness(self, all_cells: list):
        """Menambah fitness jika sel berkumpul dengan sel lain."""
        nearby_friends = 0
        for other_cell in all_cells:
            if other_cell is self:
                continue # Jangan hitung diri sendiri
            
            distance = math.hypot(self.x - other_cell.x, self.y - other_cell.y)
            if distance < JARAK_DETEKSI_SOSIAL:
                nearby_friends += 1
        
        # Jika ada lebih dari 5 sel lain di sekitar, dapatkan bonus kebugaran
        if nearby_friends >= 5:
            self.fitness += BONUS_FITNESS_SOSIAL
    
    def is_alive(self) -> bool:
        """Memeriksa apakah sel masih memiliki energi."""
        return self.energy > 0

    # =======================================================
    # Visual & Animasi Tubuh 🎨
    # =======================================================

    def _draw_body(self, screen: pygame.Surface):
        """Menggambar tubuh sel, dengan bentuk dan warna dinamis."""
        # Warna menjadi lebih cerah saat bergerak lebih cepat
        speed_ratio = self.current_speed / KECEPATAN_MAKS_SEL if KECEPATAN_MAKS_SEL > 0 else 0
        r = int(self.base_color[0] + (255 - self.base_color[0]) * speed_ratio)
        g = int(self.base_color[1] + (220 - self.base_color[1]) * speed_ratio)
        b = int(self.base_color[2] + (0 - self.base_color[2]) * speed_ratio)
        current_color = (np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255))

        # Bentuk berbeda untuk jantan dan betina
        if self.gender == 'male':
            rect = pygame.Rect(self.x - RADIUS_SEL * 1.2, self.y - RADIUS_SEL * 0.8, RADIUS_SEL * 2.4, RADIUS_SEL * 1.6)
            pygame.draw.ellipse(screen, self.outline_color, rect.inflate(2, 2))
            pygame.draw.ellipse(screen, current_color, rect)
        else:
            pygame.draw.circle(screen, self.outline_color, (int(self.x), int(self.y)), RADIUS_SEL + 1)
            pygame.draw.circle(screen, current_color, (int(self.x), int(self.y)), RADIUS_SEL)
    
    def _draw_legs(self, screen: pygame.Surface):
        """Menggambar kaki sel yang beranimasi."""
        leg_color = (40, 40, 40)
        leg_width = 3
        # Hitung ayunan kaki saat ini berdasarkan siklus animasi
        current_swing = math.sin(math.radians(self.leg_animation_cycle)) * self.leg_swing_arc
        
        # Kaki kiri
        angle1 = self.angle + math.pi / 2 + current_swing
        end_x1 = self.x + self.leg_length * math.cos(angle1)
        end_y1 = self.y + self.leg_length * math.sin(angle1)
        pygame.draw.line(screen, leg_color, (self.x, self.y), (end_x1, end_y1), leg_width)

        # Kaki kanan
        angle2 = self.angle - math.pi / 2 - current_swing
        end_x2 = self.x + self.leg_length * math.cos(angle2)
        end_y2 = self.y + self.leg_length * math.sin(angle2)
        pygame.draw.line(screen, leg_color, (self.x, self.y), (end_x2, end_y2), leg_width)
    
    def _update_legs(self):
        """Memperbarui siklus animasi kaki berdasarkan kecepatan."""
        animation_speed = self.current_speed * 2.5
        self.leg_animation_cycle = (self.leg_animation_cycle + animation_speed) % 360
    
    # =======================================================
    # Elemen UI & Debugging 📊
    # =======================================================

    def _draw_direction_indicator(self, screen: pygame.Surface):
        """Menggambar garis yang menunjukkan arah hadap sel."""
        end_x = self.x + (RADIUS_SEL + 2) * math.cos(self.angle)
        end_y = self.y + (RADIUS_SEL + 2) * math.sin(self.angle)
        pygame.draw.line(screen, (255, 50, 50), (self.x, self.y), (end_x, end_y), 2)

    def _draw_energy_bar(self, screen: pygame.Surface):
        """Menggambar bar energi di bawah sel."""
        if not self.is_alive(): return
        energy_ratio = self.energy / ENERGI_AWAL
        bar_width = RADIUS_SEL * 2
        bar_height = 4
        bar_x = self.x - RADIUS_SEL
        bar_y = self.y + RADIUS_SEL + 4
        
        # Latar belakang bar
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=1)
        
        # Warna bar (dari hijau ke merah)
        r = int(255 * (1 - energy_ratio))
        g = int(255 * energy_ratio)
        energy_color = (np.clip(r, 0, 255), np.clip(g, 0, 255), 0)
        
        # Isi bar
        fill_width = bar_width * energy_ratio
        if fill_width > 0:
            pygame.draw.rect(screen, energy_color, (bar_x, bar_y, fill_width, bar_height), border_radius=1)
    
    def _draw_fitness_bar(self, screen: pygame.Surface):
        """Menggambar bar kebugaran di bawah sel."""
        if not self.is_alive(): return
        # Normalisasi fitness untuk visualisasi (misalnya, setiap 1000 poin)
        normalized_fitness = (self.fitness % 1000) / 1000.0
        
        bar_width = RADIUS_SEL * 2
        bar_height = 4
        bar_x = self.x - RADIUS_SEL
        bar_y = self.y + RADIUS_SEL + 10
        
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=1)
        
        fitness_color = (138, 43, 226) # Ungu
        
        fill_width = bar_width * normalized_fitness
        if fill_width > 0:
            pygame.draw.rect(screen, fitness_color, (bar_x, bar_y, fill_width, bar_height), border_radius=1)

    def _draw_state_text(self, screen: pygame.Surface):
        """Menampilkan huruf inisial dari status sel saat ini."""
        if not hasattr(self, 'font'):
            self.font = pygame.font.Font(None, 20) 
        
        state_initial = self.state[0].upper()
        
        text_surface = self.font.render(state_initial, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x, self.y - RADIUS_SEL - 18))
        
        # Tambahkan latar belakang gelap agar teks lebih mudah dibaca
        bg_rect = text_rect.inflate(4, 4)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect, border_radius=3)

        screen.blit(text_surface, text_rect)
    
    def _draw_foraging_line(self, screen: pygame.Surface):
        """Menggambar garis ke target makanan jika dalam status mencari makan."""
        if self.state == 'foraging' and self.target_grass:
            distance = math.hypot(self.target_grass.x - self.x, self.target_grass.y - self.y)
            # Hanya gambar garis jika cukup dekat
            if distance < JARAK_DETEKSI_MAKANAN:
                line_color = (255, 255, 0) # Kuning
                pygame.draw.line(screen, line_color, (self.x, self.y), (self.target_grass.x, self.target_grass.y), 1)