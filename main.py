# main.py

import pygame
import math
from settings import *
from cell import Cell, NeuralNetwork
from crystal import Crystal
import random

def evolve_population(fittest_cells):
    """Menciptakan generasi baru dari sel-sel terbaik."""
    new_generation = []
    
    # Ambil otak dari sel-sel terbaik
    parent_brains = [cell.brain for cell in fittest_cells]
    
    while len(new_generation) < JUMLAH_SEL_AWAL:
        # Pilih dua orang tua secara acak dari yang terbaik
        parent1 = random.choice(parent_brains)
        parent2 = random.choice(parent_brains)
        
        # Lakukan crossover untuk membuat 'otak' anak
        child_brain = NeuralNetwork.crossover(parent1, parent2)
        
        # Lakukan mutasi pada 'otak' anak
        child_brain.mutate(MUTATION_RATE, MUTATION_STRENGTH)
        
        new_generation.append(Cell(brain=child_brain))
        
    return new_generation

def main():
    """Fungsi utama untuk menjalankan simulasi evolusi."""
    pygame.init()
    screen = pygame.display.set_mode((LEBAR_LAYAR, TINGGI_LAYAR))
    pygame.display.set_caption("Simulasi Evolusi ANN")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)

    # Inisialisasi populasi
    cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
    crystals = [Crystal() for _ in range(JUMLAH_KRISTAL)]
    
    generation_count = 1
    generation_timer = 0
    generation_frame_limit = GENERATION_TIME_SECS * FRAME_RATE
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        generation_timer += 1
        
        # --- Evolusi jika waktu generasi habis ---
        if generation_timer >= generation_frame_limit or not cells:
            generation_count += 1
            generation_timer = 0
            
            # Seleksi: Pilih sel terbaik berdasarkan fitness (umur) dan sisa energi
            cells.sort(key=lambda c: c.fitness, reverse=True)
            num_to_select = int(len(cells) * SELECTION_PERCENT)
            fittest_cells = cells[:num_to_select]
            
            # Filter lagi: hanya yang punya cukup energi yang boleh bereproduksi
            reproducers = [c for c in fittest_cells if c.energy > 0]
            
            if not reproducers: # Jika tidak ada yang selamat
                print(f"Generasi {generation_count-1} punah. Memulai dari awal.")
                cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
            else:
                print(f"Generasi {generation_count-1} -> {generation_count}. {len(reproducers)} sel berevolusi.")
                cells = evolve_population(reproducers)

        # --- Update & Logika Game ---
        for cell in cells[:]: # Gunakan salinan untuk iterasi
            if cell.update(crystals) == "mati":
                cells.remove(cell)
                continue
            
            # Cek tabrakan dengan kristal
            for crystal in crystals[:]:
                if math.hypot(cell.x - crystal.x, cell.y - crystal.y) < RADIUS_SEL + RADIUS_KRISTAL:
                    cell.energy = min(ENERGI_AWAL * 2, cell.energy + ENERGI_DARI_KRISTAL)
                    crystals.remove(crystal)
                    # crystals.append(Crystal())
                    break

        # --- Menggambar ---
        screen.fill(WARNA_LATAR)
        for c in crystals: c.draw(screen)
        for c in cells: c.draw(screen)
        
        # Teks Info
        info_gen = font.render(f"Generasi: {generation_count}", True, WARNA_TEKS)
        info_sel = font.render(f"Jumlah Sel: {len(cells)}", True, WARNA_TEKS)
        info_time = font.render(f"Waktu: {generation_timer // FRAME_RATE}s", True, WARNA_TEKS)
        screen.blit(info_gen, (10, 10))
        screen.blit(info_sel, (10, 40))
        screen.blit(info_time, (10, 70))
        
        pygame.display.flip()
        clock.tick(FRAME_RATE)

    pygame.quit()

if __name__ == "__main__":
    main()