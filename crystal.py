# crystal.py

import pygame
import random
from settings import *

class Crystal:
    """Mewakili kristal energi."""
    def __init__(self):
        self.x = random.randint(0, LEBAR_LAYAR)
        self.y = random.randint(0, TINGGI_LAYAR)

    def draw(self, screen):
        """Menggambar kristal."""
        pygame.draw.circle(screen, WARNA_KRISTAL, (self.x, self.y), RADIUS_KRISTAL)