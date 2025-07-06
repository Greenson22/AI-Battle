# grass.py

import pygame
import random
import math
from settings import *

class Grass:
    """Mendefinisikan sepetak rumput sebagai sumber makanan dengan visual yang lebih baik."""
    def __init__(self):
        # Posisi acak untuk setiap petak rumput
        self.x = random.randint(0, LEBAR_LAYAR)
        self.y = random.randint(0, TINGGI_LAYAR)
        # Radius untuk deteksi tabrakan
        self.radius = RADIUS_RUMPUT

        # Atribut untuk tampilan visual yang lebih baik
        self.num_blades = random.randint(4, 7) # Jumlah helai per rumpun
        self.blades = []
        for _ in range(self.num_blades):
            # Variasi sudut agar terlihat lebih alami
            angle = random.uniform(-math.pi / 4, math.pi / 4)
            # Variasi panjang helai
            length = self.radius * random.uniform(1.5, 2.5)
            # Sedikit variasi warna untuk kedalaman
            color_variation = random.randint(-20, 20)
            color = (
                max(0, min(255, WARNA_RUMPUT[0] + color_variation)),
                max(0, min(255, WARNA_RUMPUT[1] + color_variation)),
                max(0, min(255, WARNA_RUMPUT[2] + color_variation))
            )
            self.blades.append({'angle': angle, 'length': length, 'color': color})

    def draw(self, screen):
        """Menggambar beberapa helai rumput untuk menciptakan tampilan yang lebih rimbun."""
        for blade in self.blades:
            # Titik akhir untuk setiap helai rumput, dimulai dari dasar (y) ke atas
            end_x = self.x + math.sin(blade['angle']) * blade['length']
            end_y = self.y - math.cos(blade['angle']) * blade['length']
            
            # Menggambar garis tebal sebagai helai rumput
            pygame.draw.line(screen, blade['color'], (self.x, self.y), (end_x, end_y), 2)