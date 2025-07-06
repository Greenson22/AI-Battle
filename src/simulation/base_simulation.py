# src/simulation/base_simulation.py

import pygame
import sys
import math
from settings import *
from crystal import Crystal

class BaseSimulation:
    def __init__(self, title="Simulasi"):
        self.screen = pygame.display.set_mode((LEBAR_LAYAR, TINGGI_LAYAR))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.running = True
        self.terrain = None
        self.cells = []
        self.crystals = [Crystal() for _ in range(JUMLAH_KRISTAL)]

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
            # Logika kematian karena tenggelam/kehabisan energi ada di dalam cell.update
            if cell.update(self.crystals, biome_at_cell) == "mati":
                self.cells.remove(cell)
            else:
                self._check_crystal_collision(cell)

    def _check_crystal_collision(self, cell):
        for crystal in self.crystals[:]:
            if math.hypot(cell.x - crystal.x, cell.y - crystal.y) < RADIUS_SEL + RADIUS_KRISTAL:
                cell.energy = min(ENERGI_AWAL * 2, cell.energy + ENERGI_DARI_KRISTAL)
                self.crystals.remove(crystal)
                self.crystals.append(Crystal())
                break

    # vvvv [PERUBAHAN UTAMA DI SINI] vvvv
    def _draw_elements(self):
        self.terrain.draw(self.screen)

        # Logika untuk outline Emas & Perak
        if self.cells:
            # Urutkan sel berdasarkan fitness, dari tertinggi ke terendah
            sorted_cells = sorted(self.cells, key=lambda c: c.fitness, reverse=True)
            
            # Reset semua outline ke default (hitam) terlebih dahulu
            for cell in self.cells:
                # Pastikan sel punya atribut outline_color (seharusnya sudah dari jawaban sebelumnya)
                if hasattr(cell, 'outline_color'):
                    cell.outline_color = (10, 10, 10) # Hitam

            # Atur warna outline untuk sel terbaik pertama (Emas)
            if len(sorted_cells) > 0 and hasattr(sorted_cells[0], 'outline_color'):
                sorted_cells[0].outline_color = (255, 215, 0) # Gold
            
            # Atur warna outline untuk sel terbaik kedua (Perak)
            if len(sorted_cells) > 1 and hasattr(sorted_cells[1], 'outline_color'):
                sorted_cells[1].outline_color = (192, 192, 192) # Silver
        
        # Gambar semua entitas
        for entity in self.crystals + self.cells:
            entity.draw(self.screen)
            
        self._draw_info_text()
        pygame.display.flip()
    # ^^^^ [AKHIR PERUBAHAN] ^^^^

    def _draw_info_text(self):
        info_sel = self.font.render(f"Jumlah Sel: {len(self.cells)}", True, WARNA_TEKS)
        self.screen.blit(info_sel, (10, 40))
        info_help = self.font.render("Tekan ESC untuk kembali ke menu", True, WARNA_TEKS)
        self.screen.blit(info_help, (10, TINGGI_LAYAR - 40))