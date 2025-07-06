# grass.py

import pygame
import random
from settings import *

class Grass:
    """Mendefinisikan sepetak rumput sebagai sumber makanan."""
    def __init__(self):
        # Posisi acak untuk setiap petak rumput
        self.x = random.randint(0, LEBAR_LAYAR)
        self.y = random.randint(0, TINGGI_LAYAR)
        # Radius untuk deteksi tabrakan dan ukuran gambar
        self.radius = RADIUS_RUMPUT

    def draw(self, screen):
        """Menggambar rumput sebagai segitiga hijau sederhana dan solid."""
        # Titik-titik untuk segitiga (puncak, kiri bawah, kanan bawah)
        # Ini menciptakan bentuk yang statis dan tidak berubah setiap frame.
        puncak = (self.x, self.y - self.radius)
        kiri_bawah = (self.x - self.radius, self.y + self.radius)
        kanan_bawah = (self.x + self.radius, self.y + self.radius)
        
        # Menggambar poligon (segitiga) yang diisi dengan warna rumput.
        pygame.draw.polygon(screen, WARNA_RUMPUT, [puncak, kiri_bawah, kanan_bawah])