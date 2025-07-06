# main.py

import pygame
import math
from settings import *
from cell import Cell, NeuralNetwork
from crystal import Crystal
import random

class Simulation:
    """
    Mengelola seluruh siklus hidup simulasi evolusi,
    termasuk inisialisasi, loop utama, evolusi, dan penggambaran.
    """
    def __init__(self):
        """Inisialisasi jendela Pygame dan status awal simulasi."""
        pygame.init()
        self.screen = pygame.display.set_mode((LEBAR_LAYAR, TINGGI_LAYAR))
        pygame.display.set_caption("Simulasi Evolusi ANN")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        
        self.running = True
        self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
        self.crystals = [Crystal() for _ in range(JUMLAH_KRISTAL)]
        
        self.generation_count = 1
        self.generation_timer = 0
        self.generation_frame_limit = GENERATION_TIME_SECS * FRAME_RATE

    def run(self):
        """Loop utama simulasi."""
        while self.running:
            self._handle_events()
            self._update_simulation()
            self._draw_elements()
            self.clock.tick(FRAME_RATE)
        
        pygame.quit()

    def _handle_events(self):
        """Menangani input dari pengguna, seperti menutup jendela."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def _update_simulation(self):
        """Memperbarui semua logika game dan status simulasi untuk satu frame."""
        self.generation_timer += 1
        
        # Cek apakah waktunya untuk evolusi
        if self.generation_timer >= self.generation_frame_limit or not self.cells:
            self._evolve_next_generation()

        # Update setiap sel
        for cell in self.cells[:]:
            if cell.update(self.crystals) == "mati":
                self.cells.remove(cell)
                continue
            
            # Cek tabrakan sel dengan kristal
            self._check_crystal_collision(cell)
    
    def _check_crystal_collision(self, cell):
        """Memeriksa dan menangani tabrakan antara sel dan kristal."""
        for crystal in self.crystals[:]:
            distance = math.hypot(cell.x - crystal.x, cell.y - crystal.y)
            if distance < RADIUS_SEL + RADIUS_KRISTAL:
                cell.energy = min(ENERGI_AWAL * 2, cell.energy + ENERGI_DARI_KRISTAL)
                self.crystals.remove(crystal)
                self.crystals.append(Crystal()) # Langsung buat kristal baru
                break

    def _evolve_next_generation(self):
        """Mengelola proses seleksi dan penciptaan generasi baru."""
        self.generation_count += 1
        self.generation_timer = 0
        
        # Sebarkan ulang semua kristal untuk generasi baru
        self.crystals = [Crystal() for _ in range(JUMLAH_KRISTAL)]
        
        # Seleksi sel terbaik
        self.cells.sort(key=lambda c: c.fitness, reverse=True)
        num_to_select = int(len(self.cells) * SELECTION_PERCENT)
        fittest_cells = self.cells[:num_to_select]
        
        # Filter sel yang layak bereproduksi (punya cukup energi)
        reproducers = [c for c in fittest_cells if c.energy > 0]
        
        if not reproducers:
            print(f"Generasi {self.generation_count-1} punah. Memulai dari awal.")
            self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
        else:
            print(f"Generasi {self.generation_count-1} -> {self.generation_count}. {len(reproducers)} sel berevolusi.")
            self.cells = self._create_new_population(reproducers)

    def _create_new_population(self, parent_cells):
        """Menciptakan populasi baru dari sel-sel induk terbaik."""
        new_generation = []
        parent_brains = [cell.brain for cell in parent_cells]
        
        while len(new_generation) < JUMLAH_SEL_AWAL:
            parent1 = random.choice(parent_brains)
            parent2 = random.choice(parent_brains)
            
            child_brain = NeuralNetwork.crossover(parent1, parent2)
            child_brain.mutate(MUTATION_RATE, MUTATION_STRENGTH)
            
            new_generation.append(Cell(brain=child_brain))
            
        return new_generation

    def _draw_elements(self):
        """Menggambar semua elemen visual ke layar."""
        self.screen.fill(WARNA_LATAR)
        
        for crystal in self.crystals:
            crystal.draw(self.screen)
        for cell in self.cells:
            cell.draw(self.screen)
            
        self._draw_info_text()
        
        pygame.display.flip()

    def _draw_info_text(self):
        """Menampilkan teks informasi di layar."""
        info_gen = self.font.render(f"Generasi: {self.generation_count}", True, WARNA_TEKS)
        info_sel = self.font.render(f"Jumlah Sel: {len(self.cells)}", True, WARNA_TEKS)
        info_time = self.font.render(f"Waktu: {self.generation_timer // FRAME_RATE}s", True, WARNA_TEKS)
        
        self.screen.blit(info_gen, (10, 10))
        self.screen.blit(info_sel, (10, 40))
        self.screen.blit(info_time, (10, 70))


if __name__ == "__main__":
    simulation = Simulation()
    simulation.run()