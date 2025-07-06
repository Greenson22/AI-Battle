# grass.py

import pygame
import random
import math
from settings import *

class Grass:
    """Mendefinisikan sepetak rumput statis dengan tampilan garis-garis yang unik."""
    def __init__(self, terrain):
        # Posisi acak untuk pusat rumpun rumput
        self.x = random.randint(0, LEBAR_LAYAR - 1)
        self.y = random.randint(0, TINGGI_LAYAR - 1)
        self.biome = terrain.get_biome_at(self.x, self.y)
        
        # Atur status hidup dan kesuburan berdasarkan biome
        self.alive = True
        self.thriving = False
        if self.biome in ['air', 'batu']:
            self.alive = False
        elif self.biome == 'pasir':
            self.thriving = True

        self.radius = RADIUS_RUMPUT
        self.blades = [] # List untuk menyimpan data setiap helai rumput
        self._generate_blades() # Panggil fungsi untuk membuat helai-helai rumput

    def _generate_blades(self):
        """Membuat dan menyimpan properti setiap helai rumput secara permanen."""
        if not self.alive:
            return
            
        num_blades = random.randint(4, 8)

        # Tentukan properti berdasarkan kesuburan rumput
        if self.thriving:
            base_color = (107, 222, 0) # Warna lebih cerah
            blade_length = self.radius * 1.5
            line_width = 2
        else:
            base_color = WARNA_RUMPUT
            blade_length = self.radius
            line_width = 1

        for _ in range(num_blades):
            # Titik pangkal untuk setiap helai
            start_x = self.x + random.randint(-self.radius // 2, self.radius // 2)
            start_y = self.y + random.randint(0, self.radius // 3)

            # Hitung titik ujung dengan sudut dan panjang acak
            angle = math.radians(random.randint(250, 290))
            current_length = blade_length * random.uniform(0.8, 1.2)
            end_x = start_x + math.cos(angle) * current_length
            end_y = start_y + math.sin(angle) * current_length
            
            # Variasi warna alami
            color_variation = random.randint(-20, 20)
            r = max(0, min(255, base_color[0] + color_variation))
            g = max(0, min(255, base_color[1] + color_variation))
            b = max(0, min(255, base_color[2] + color_variation))
            blade_color = (r, g, b)
            
            # Simpan data helai rumput (titik awal, titik akhir, warna, tebal)
            self.blades.append(((start_x, start_y), (end_x, end_y), blade_color, line_width))

    def draw(self, screen):
        """Menggambar helai-helai rumput yang sudah disimpan."""
        if not self.alive:
            return

        # Gambar setiap helai rumput dari data yang sudah ada
        for start_pos, end_pos, color, width in self.blades:
            pygame.draw.line(screen, color, start_pos, end_pos, width)