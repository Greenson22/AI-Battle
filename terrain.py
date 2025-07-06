# terrain.py

import pygame
import numpy as np
from perlin_noise import PerlinNoise
import os
from settings import *

class Terrain:
    def __init__(self, width, height, scale=TERRAIN_SCALE, octaves=6, seed=None):
        self.width = width
        self.height = height
        self.scale = scale
        self.octaves = octaves
        self.seed = seed if seed is not None else np.random.randint(0, 100)

        self.terrain_map = self.load_map_data(WORLD_FILE)
        self.terrain_surface = self.load_map_image(WORLD_IMAGE_FILE)

        if self.terrain_map is None or self.terrain_surface is None:
            print("Membuat data terrain baru (mungkin perlu beberapa saat)...")
            self.terrain_map = self.generate_world()
            self.terrain_surface = self.create_terrain_surface_optimized()
            self.save_world()

    # vvv FUNGSI DIPERBAIKI vvv
    def generate_world(self):
        """Membuat peta noise. Kembali menggunakan loop karena .map tidak ada."""
        noise = PerlinNoise(octaves=self.octaves, seed=self.seed)
        world = np.zeros((self.width, self.height))
        # Perulangan ini memang lebih lambat, tapi hanya dijalankan sekali
        for i in range(self.width):
            for j in range(self.height):
                world[i][j] = noise([i / self.scale, j / self.scale])
        
        world = (world - np.min(world)) / (np.max(world) - np.min(world))
        return world
    # ^^^ FUNGSI DIPERBAIKI ^^^

    def create_terrain_surface_optimized(self):
        """Membuat surface menggunakan NumPy (Sangat Cepat)."""
        image_array = np.zeros((self.width, self.height, 3), dtype=np.uint8)
        image_array[self.terrain_map < TINGKAT_AIR] = WARNA_TERRAIN['air']
        image_array[(self.terrain_map >= TINGKAT_AIR) & (self.terrain_map < TINGKAT_PASIR)] = WARNA_TERRAIN['pasir']
        image_array[(self.terrain_map >= TINGKAT_PASIR) & (self.terrain_map < TINGKAT_RUMPUT)] = WARNA_TERRAIN['rumput']
        image_array[(self.terrain_map >= TINGKAT_RUMPUT) & (self.terrain_map < TINGKAT_HUTAN)] = WARNA_TERRAIN['hutan']
        image_array[self.terrain_map >= TINGKAT_HUTAN] = WARNA_TERRAIN['batu']
        return pygame.surfarray.make_surface(image_array)

    def get_biome_at(self, x, y):
        """Mendapatkan tipe biome pada koordinat x, y."""
        if 0 <= x < self.width and 0 <= y < self.height:
            val = self.terrain_map[int(x)][int(y)]
            if val < TINGKAT_AIR: return 'air'
            if val < TINGKAT_PASIR: return 'pasir'
            if val < TINGKAT_RUMPUT: return 'rumput'
            if val < TINGKAT_HUTAN: return 'hutan'
            return 'batu'
        return 'batu' # Default jika di luar batas

    def draw(self, screen):
        screen.blit(self.terrain_surface, (0, 0))

    def save_world(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        np.save(WORLD_FILE, self.terrain_map)
        pygame.image.save(self.terrain_surface, WORLD_IMAGE_FILE)
        print(f"Dunia (data & gambar) berhasil disimpan.")

    def load_map_data(self, filename):
        if os.path.exists(filename):
            return np.load(filename)
        return None

    def load_map_image(self, filename):
        if os.path.exists(filename):
            print(f"Memuat gambar peta dari {filename} (CEPAT)...")
            return pygame.image.load(filename).convert()
        return None

    @classmethod
    def create_new_world(cls, width, height):
        if os.path.exists(WORLD_FILE): os.remove(WORLD_FILE)
        if os.path.exists(WORLD_IMAGE_FILE): os.remove(WORLD_IMAGE_FILE)
        return cls(width, height)