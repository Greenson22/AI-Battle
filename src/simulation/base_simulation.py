# src/simulation/base_simulation.py

import pygame
import sys
import math
from settings import *
from grass import Grass

class BaseSimulation:
    def __init__(self, title="Simulasi"):
        self.screen = pygame.display.set_mode((LEBAR_LAYAR, TINGGI_LAYAR))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.running = True
        self.terrain = None
        self.cells = []
        # Kosongkan grass_patches di sini, akan diisi nanti
        self.grass_patches = []

    def run(self):
        if self.terrain is None:
            print("Error: Terrain belum diatur untuk simulasi ini!")
            return
            
        # Pindahkan inisialisasi rumput ke sini agar 'terrain' sudah ada
        if not self.grass_patches:
             while len(self.grass_patches) < JUMLAH_RUMPUT:
                new_grass = Grass(self.terrain)
                if new_grass.alive:
                    self.grass_patches.append(new_grass)

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
            if cell.update(self.grass_patches, biome_at_cell) == "mati":
                self.cells.remove(cell)
            else:
                self._check_grass_collision(cell)

    def _check_grass_collision(self, cell):
        """Memeriksa tabrakan sel dan rumput, lalu menumbuhkan rumput baru di tempat valid."""
        for grass in self.grass_patches[:]:
            if math.hypot(cell.x - grass.x, cell.y - grass.y) < RADIUS_SEL + grass.radius:
                cell.energy = min(ENERGI_AWAL * 2, cell.energy + ENERGI_DARI_RUMPUT)
                self.grass_patches.remove(grass)
                
                # Loop untuk memastikan rumput baru tumbuh di daratan yang valid
                new_grass = None
                while new_grass is None or not new_grass.alive:
                    new_grass = Grass(self.terrain)
                self.grass_patches.append(new_grass)
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
        
        for entity in self.grass_patches + self.cells:
            entity.draw(self.screen)
            
        self._draw_info_text()
        pygame.display.flip()

    def _draw_info_text(self):
        info_sel = self.font.render(f"Jumlah Sel: {len(self.cells)}", True, WARNA_TEKS)
        self.screen.blit(info_sel, (10, 40))
        info_help = self.font.render("Tekan ESC untuk kembali ke menu", True, WARNA_TEKS)
        self.screen.blit(info_help, (10, TINGGI_LAYAR - 40))