# src/simulation/base_simulation.py

import pygame
import sys
import math
from settings import *
from grass import Grass # <-- Import Grass, bukan Crystal

class BaseSimulation:
    def __init__(self, title="Simulasi"):
        self.screen = pygame.display.set_mode((LEBAR_LAYAR, TINGGI_LAYAR))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.running = True
        self.terrain = None
        self.cells = []
        # Ganti self.crystals menjadi self.grass_patches
        self.grass_patches = [Grass() for _ in range(JUMLAH_RUMPUT)]

    def run(self):
        if self.terrain is None:
            print("Error: Terrain belum diatur untuk simulasi ini!")
            return
        while self.running:
            self._handle_events()
            self._update_simulation()
            self._draw_elements()
            self.clock.tick(FRAME_RATE)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                self._handle_key_press(event)

    def _handle_key_press(self, event):
        pass

    def _update_simulation(self):
        for cell in self.cells[:]:
            biome_at_cell = self.terrain.get_biome_at(cell.x, cell.y)
            # Berikan list rumput ke fungsi update
            if cell.update(self.grass_patches, biome_at_cell) == "mati":
                self.cells.remove(cell)
            else:
                self._check_grass_collision(cell) # Panggil fungsi tabrakan rumput

    def _check_grass_collision(self, cell):
        """Memeriksa dan menangani tabrakan antara sel dan rumput."""
        for grass in self.grass_patches[:]:
            # Deteksi tabrakan berdasarkan jarak (lebih akurat untuk lingkaran)
            if math.hypot(cell.x - grass.x, cell.y - grass.y) < RADIUS_SEL + RADIUS_RUMPUT:
                cell.energy = min(ENERGI_AWAL * 2, cell.energy + ENERGI_DARI_RUMPUT)
                self.grass_patches.remove(grass)
                # Tambahkan rumput baru di lokasi acak
                self.grass_patches.append(Grass())
                break

    def _draw_elements(self):
        self.terrain.draw(self.screen)

        if self.cells:
            sorted_cells = sorted(self.cells, key=lambda c: c.fitness, reverse=True)
            for cell in self.cells:
                if hasattr(cell, 'outline_color'):
                    cell.outline_color = (10, 10, 10)
            if len(sorted_cells) > 0 and hasattr(sorted_cells[0], 'outline_color'):
                sorted_cells[0].outline_color = (255, 215, 0)
            if len(sorted_cells) > 1 and hasattr(sorted_cells[1], 'outline_color'):
                sorted_cells[1].outline_color = (192, 192, 192)
        
        # Gambar semua rumput dan sel
        for entity in self.grass_patches + self.cells:
            entity.draw(self.screen)
            
        self._draw_info_text()
        pygame.display.flip()

    def _draw_info_text(self):
        info_sel = self.font.render(f"Jumlah Sel: {len(self.cells)}", True, WARNA_TEKS)
        self.screen.blit(info_sel, (10, 40))
        info_help = self.font.render("Tekan ESC untuk kembali ke menu", True, WARNA_TEKS)
        self.screen.blit(info_help, (10, TINGGI_LAYAR - 40))