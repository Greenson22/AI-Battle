# main.py (Diperbaiki)

import pygame
import math
import random
import sys
from settings import *
from cell import Cell, NeuralNetwork
from crystal import Crystal

# Kelas Button tidak berubah
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, screen, font):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        text_surf = font.render(self.text, True, WARNA_TEKS)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered

# Kelas MainMenu tidak berubah
class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 50)
        self.running = True
        
        btn_width, btn_height = 300, 60
        btn_x = (LEBAR_LAYAR - btn_width) / 2
        
        self.buttons = {
            "train": Button(btn_x, 200, btn_width, btn_height, "Mulai Latihan", (0, 100, 200), (0, 150, 255)),
            "sandbox": Button(btn_x, 280, btn_width, btn_height, "Buka Sandbox", (0, 150, 100), (0, 200, 150)),
            "quit": Button(btn_x, 360, btn_width, btn_height, "Keluar", (200, 50, 50), (255, 100, 100))
        }

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                for mode, button in self.buttons.items():
                    if button.is_clicked(event):
                        return mode
            for button in self.buttons.values():
                button.check_hover(mouse_pos)

            self.screen.fill(WARNA_LATAR)
            title_surf = self.font.render("Simulasi Evolusi Sel", True, WARNA_TEKS)
            title_rect = title_surf.get_rect(center=(LEBAR_LAYAR/2, 100))
            self.screen.blit(title_surf, title_rect)
            for button in self.buttons.values():
                button.draw(self.screen, self.font)
            pygame.display.flip()
        return "quit"


class BaseSimulation:
    def __init__(self, title="Simulasi"):
        # Kesalahan dari prompt sebelumnya sudah diperbaiki di sini
        self.screen = pygame.display.set_mode((LEBAR_LAYAR, TINGGI_LAYAR))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.running = True
        self.cells = []
        self.crystals = [Crystal() for _ in range(JUMLAH_KRISTAL)]

    def run(self):
        """Loop utama simulasi untuk satu mode."""
        while self.running:
            self._handle_events()
            self._update_simulation()
            self._draw_elements()
            self.clock.tick(FRAME_RATE)
        # ❗ PERBAIKAN: Hapus pygame.quit() dari sini
        # pygame.quit() # <-- BARIS INI DIHAPUS

    # ... sisa metode di BaseSimulation tidak berubah ...
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def _update_simulation(self):
        for cell in self.cells[:]:
            if cell.update(self.crystals) == "mati":
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

    def _draw_elements(self):
        self.screen.fill(WARNA_LATAR)
        for entity in self.crystals + self.cells:
            entity.draw(self.screen)
        self._draw_info_text()
        pygame.display.flip()

    def _draw_info_text(self):
        info_sel = self.font.render(f"Jumlah Sel: {len(self.cells)}", True, WARNA_TEKS)
        self.screen.blit(info_sel, (10, 40))
        info_help = self.font.render("Tekan ESC untuk kembali ke menu", True, WARNA_TEKS)
        self.screen.blit(info_help, (10, TINGGI_LAYAR - 40))

# Kelas TrainingMode dan SandboxMode tidak ada perubahan
class TrainingMode(BaseSimulation):
    def __init__(self):
        super().__init__(title="Mode Latihan")
        self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
        self.generation_count = 1
        self.generation_timer = 0
        self.generation_frame_limit = GENERATION_TIME_SECS * FRAME_RATE
        
    def _handle_events(self):
        super()._handle_events()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self._save_fittest_brains()

    def _update_simulation(self):
        super()._update_simulation()
        self.generation_timer += 1
        if self.generation_timer >= self.generation_frame_limit or not self.cells:
            self._evolve_next_generation()

    def _evolve_next_generation(self):
        self.generation_count += 1
        self.generation_timer = 0
        self.crystals = [Crystal() for _ in range(JUMLAH_KRISTAL)]
        
        self.cells.sort(key=lambda c: c.fitness, reverse=True)
        num_to_select = int(len(self.cells) * SELECTION_PERCENT)
        fittest_cells = self.cells[:num_to_select]
        reproducers = [c for c in fittest_cells if c.energy > 0]
        
        if not reproducers:
            print(f"Generasi {self.generation_count-1} punah.")
            self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
        else:
            print(f"Generasi {self.generation_count-1} -> {self.generation_count}.")
            brains_to_reproduce = [c.brain for c in reproducers]
            self.cells = self._create_new_population(brains_to_reproduce)

    def _create_new_population(self, parent_brains):
        new_generation = []
        while len(new_generation) < JUMLAH_SEL_AWAL:
            p1 = random.choice(parent_brains)
            p2 = random.choice(parent_brains)
            child_brain = NeuralNetwork.crossover(p1, p2)
            child_brain.mutate(MUTATION_RATE, MUTATION_STRENGTH)
            new_generation.append(Cell(brain=child_brain))
        return new_generation
        
    def _save_fittest_brains(self):
        if not self.cells:
            print("Tidak ada sel untuk disimpan.")
            return
        self.cells.sort(key=lambda c: c.fitness, reverse=True)
        num_to_save = min(len(self.cells), 10)
        fittest_brains = [cell.brain for cell in self.cells[:num_to_save]]
        NeuralNetwork.save_brains(BRAIN_FILE, fittest_brains)

    def _draw_info_text(self):
        super()._draw_info_text()
        info_gen = self.font.render(f"Generasi: {self.generation_count}", True, WARNA_TEKS)
        info_time = self.font.render(f"Waktu: {self.generation_timer // FRAME_RATE}s", True, WARNA_TEKS)
        info_save = self.font.render("Tekan 'S' untuk menyimpan sel terbaik", True, WARNA_TEKS)
        self.screen.blit(info_gen, (10, 10))
        self.screen.blit(info_time, (10, 70))
        self.screen.blit(info_save, (LEBAR_LAYAR - info_save.get_width() - 10, 10))

class SandboxMode(BaseSimulation):
    def __init__(self):
        super().__init__(title="Mode Sandbox")
        trained_brains = NeuralNetwork.load_brains(BRAIN_FILE)
        if not trained_brains:
            print("Gagal memuat otak. Sandbox dimulai dengan sel acak.")
            self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
        else:
            for i in range(JUMLAH_SEL_AWAL):
                brain_to_use = random.choice(trained_brains)
                self.cells.append(Cell(brain=brain_to_use))


def main():
    """Fungsi utama untuk menjalankan aplikasi."""
    pygame.init() # Cukup panggil sekali di sini
    screen = pygame.display.set_mode((LEBAR_LAYAR, TINGGI_LAYAR))
    
    while True:
        menu = MainMenu(screen)
        choice = menu.run()

        if choice == "train":
            game = TrainingMode()
            game.run()
        elif choice == "sandbox":
            game = SandboxMode()
            game.run()
        elif choice == "quit":
            break # Keluar dari loop utama

    # Panggil quit sekali saja, sebelum aplikasi benar-benar ditutup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()