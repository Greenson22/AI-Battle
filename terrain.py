# terrain.py
import pygame
import numpy as np
from perlin_noise import PerlinNoise
import os
from settings import * # Pastikan semua pengaturan ter-import

class Terrain:
    # vvv UBAH BARIS INI vvv
    def __init__(self, width, height, scale=TERRAIN_SCALE, octaves=6, persistence=0.5, lacunarity=2.0, seed=None):
    # ^^^ UBAH BARIS INI ^^^
        self.width = width
        self.height = height
        # Parameter 'scale' sekarang menggunakan nilai default dari settings.py
        self.scale = scale
        self.octaves = octaves
        self.seed = seed if seed is not None else np.random.randint(0, 100)
        self.terrain_map = self.generate_world()
        self.terrain_surface = self.create_terrain_surface()

    def generate_world(self):
        noise = PerlinNoise(octaves=self.octaves, seed=self.seed)
        
        world = np.zeros((self.width, self.height))
        for i in range(self.width):
            for j in range(self.height):
                # Pemanggilan noise menggunakan self.scale yang sudah diperbarui
                world[i][j] = noise([i / self.scale, j / self.scale])
                
        world = (world - np.min(world)) / (np.max(world) - np.min(world))
        return world

    # ... (sisa kelas tidak berubah) ...
    def get_biome(self, value):
        if value < TINGKAT_AIR: return 'air'
        elif value < TINGKAT_PASIR: return 'pasir'
        elif value < TINGKAT_RUMPUT: return 'rumput'
        elif value < TINGKAT_HUTAN: return 'hutan'
        else: return 'batu'

    def create_terrain_surface(self):
        surface = pygame.Surface((self.width, self.height))
        for i in range(self.width):
            for j in range(self.height):
                noise_val = self.terrain_map[i][j]
                biome = self.get_biome(noise_val)
                color = WARNA_TERRAIN[biome]
                surface.set_at((i, j), color)
        return surface

    def draw(self, screen):
        screen.blit(self.terrain_surface, (0, 0))

    def get_terrain_type_at(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            val = self.terrain_map[int(x)][int(y)]
            return self.get_biome(val)
        return 'batu'

    def save_world(self, filename="data/world.npy"):
        if not os.path.exists('data'):
            os.makedirs('data')
        np.save(filename, self.terrain_map)
        print(f" Dunia berhasil disimpan ke {filename}")

    @classmethod
    def load_world(cls, filename="data/world.npy"):
        if os.path.exists(filename):
            terrain_map = np.load(filename)
            width, height = terrain_map.shape
            terrain = cls(width, height)
            terrain.terrain_map = terrain_map
            terrain.terrain_surface = terrain.create_terrain_surface()
            print(f" Dunia berhasil dimuat dari {filename}")
            return terrain
        return None