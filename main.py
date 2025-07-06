# main.py

# ... (semua kelas Menu dan Button tidak berubah) ...
# ...
import pygame
import math
import random
import sys
import numpy as np
import os
from settings import *
from cell import Cell, NeuralNetwork
from crystal import Crystal
from terrain import Terrain

def show_loading_screen(screen, text="Memuat..."):
    font_loading = pygame.font.Font(None, 74)
    screen.fill(WARNA_LATAR)
    text_surf = font_loading.render(text, True, WARNA_TEKS)
    text_rect = text_surf.get_rect(center=(LEBAR_LAYAR / 2, TINGGI_LAYAR / 2))
    screen.blit(text_surf, text_rect)
    pygame.display.flip()

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

class BaseMenu:
    def __init__(self, screen, title):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 60)
        self.font_button = pygame.font.Font(None, 50)
        self.running = True
        self.title = title
        self.buttons = {}
    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "quit_app"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    return "back"
                for mode, button in self.buttons.items():
                    if button.is_clicked(event):
                        self.running = False
                        return mode
            for button in self.buttons.values():
                button.check_hover(mouse_pos)
            self.draw()
            pygame.display.flip()
        return "back"
    def draw(self):
        self.screen.fill(WARNA_LATAR)
        title_surf = self.font_title.render(self.title, True, WARNA_TEKS)
        title_rect = title_surf.get_rect(center=(LEBAR_LAYAR / 2, 100))
        self.screen.blit(title_surf, title_rect)
        for button in self.buttons.values():
            button.draw(self.screen, self.font_button)

class MainMenu(BaseMenu):
    def __init__(self, screen):
        super().__init__(screen, "Simulasi Evolusi Sel")
        btn_width, btn_height = 350, 60
        btn_x = (LEBAR_LAYAR - btn_width) / 2
        self.buttons = {
            "train": Button(btn_x, 200, btn_width, btn_height, "Mulai Latihan", (0, 100, 200), (0, 150, 255)),
            "sandbox": Button(btn_x, 280, btn_width, btn_height, "Buka Sandbox", (0, 150, 100), (0, 200, 150)),
            "world_menu": Button(btn_x, 360, btn_width, btn_height, "Pengaturan Dunia", (100, 100, 100), (150, 150, 150)),
            "quit": Button(btn_x, 440, btn_width, btn_height, "Keluar", (200, 50, 50), (255, 100, 100))
        }

class TrainingStartMenu(BaseMenu):
    def __init__(self, screen):
        super().__init__(screen, "Mode Latihan")
        btn_width, btn_height = 400, 60
        btn_x = (LEBAR_LAYAR - btn_width) / 2
        self.buttons = {
            "new_training": Button(btn_x, 200, btn_width, btn_height, "Mulai dari Awal", (20, 140, 180), (30, 160, 200)),
            "continue_training": Button(btn_x, 280, btn_width, btn_height, "Lanjutkan dari File", (20, 180, 140), (30, 200, 160)),
        }

class WorldMenu(BaseMenu):
    def __init__(self, screen):
        super().__init__(screen, "Pengaturan Dunia")
        btn_width, btn_height = 450, 60
        btn_x = (LEBAR_LAYAR - btn_width) / 2
        self.buttons = {
            "generate_world": Button(btn_x, 200, btn_width, btn_height, "Buat & Simpan Dunia Baru", (20, 140, 180), (30, 160, 200)),
            "back": Button(btn_x, 280, btn_width, btn_height, "Kembali", (100, 100, 100), (150, 150, 150)),
        }

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

    # vvv FUNGSI DIPERBAIKI vvv
    def _update_simulation(self):
        for cell in self.cells[:]:
            # Dapatkan nama biome sekali saja di sini
            biome_at_cell = self.terrain.get_biome_at(cell.x, cell.y)
            # Kirim nama biome (string) ke metode update sel
            if cell.update(self.crystals, biome_at_cell) == "mati":
                self.cells.remove(cell)
            else:
                self._check_crystal_collision(cell)
    # ^^^ FUNGSI DIPERBAIKI ^^^

    def _check_crystal_collision(self, cell):
        for crystal in self.crystals[:]:
            if math.hypot(cell.x - crystal.x, cell.y - crystal.y) < RADIUS_SEL + RADIUS_KRISTAL:
                cell.energy = min(ENERGI_AWAL * 2, cell.energy + ENERGI_DARI_KRISTAL)
                self.crystals.remove(crystal)
                self.crystals.append(Crystal())
                break
    
    def _draw_elements(self):
        self.terrain.draw(self.screen)
        for entity in self.crystals + self.cells:
            entity.draw(self.screen)
        self._draw_info_text()
        pygame.display.flip()
    
    def _draw_info_text(self):
        info_sel = self.font.render(f"Jumlah Sel: {len(self.cells)}", True, WARNA_TEKS)
        self.screen.blit(info_sel, (10, 40))
        info_help = self.font.render("Tekan ESC untuk kembali ke menu", True, WARNA_TEKS)
        self.screen.blit(info_help, (10, TINGGI_LAYAR - 40))

class TrainingMode(BaseSimulation):
    # ... (Kelas TrainingMode tidak ada perubahan) ...
    def __init__(self, start_from_scratch=True):
        super().__init__(title="Mode Latihan")
        self.generation_count = 1
        self.generation_timer = 0
        self.generation_frame_limit = GENERATION_TIME_SECS * FRAME_RATE
        self.save_indicator_timer = 0
        if start_from_scratch:
            self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
        else:
            trained_brains = NeuralNetwork.load_brains(BRAIN_FILE)
            if not trained_brains:
                self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
            else:
                self.cells = self._create_new_population(trained_brains)
    def _handle_key_press(self, event):
        if event.key == pygame.K_s: self._save_fittest_brains()
    def _update_simulation(self):
        super()._update_simulation()
        self.generation_timer += 1
        if self.save_indicator_timer > 0: self.save_indicator_timer -= 1
        if self.generation_timer >= self.generation_frame_limit or not self.cells: self._evolve_next_generation()
    def _save_fittest_brains(self):
        if not self.cells: return
        self.cells.sort(key=lambda c: c.fitness, reverse=True)
        fittest_brains = [cell.brain for cell in self.cells[:10]]
        NeuralNetwork.save_brains(BRAIN_FILE, fittest_brains)
        self.save_indicator_timer = 120
    def _draw_info_text(self):
        super()._draw_info_text()
        info_gen = self.font.render(f"Generasi: {self.generation_count}", True, WARNA_TEKS)
        info_time = self.font.render(f"Waktu: {self.generation_timer // FRAME_RATE}s", True, WARNA_TEKS)
        info_save_prompt = self.font.render("Tekan 'S' untuk menyimpan", True, WARNA_TEKS)
        self.screen.blit(info_gen, (10, 10))
        self.screen.blit(info_time, (10, 70))
        self.screen.blit(info_save_prompt, (LEBAR_LAYAR - info_save_prompt.get_width() - 10, 10))
        if self.save_indicator_timer > 0:
            save_indicator_text = self.font.render("Otak berhasil disimpan!", True, (100, 255, 100))
            text_rect = save_indicator_text.get_rect(topright=(LEBAR_LAYAR - 10, 40))
            self.screen.blit(save_indicator_text, text_rect)
    def _evolve_next_generation(self):
        self.generation_count += 1
        self.generation_timer = 0
        self.crystals = [Crystal() for _ in range(JUMLAH_KRISTAL)]
        self.cells.sort(key=lambda c: c.fitness, reverse=True)
        num_to_select = int(len(self.cells) * SELECTION_PERCENT)
        fittest_cells = self.cells[:num_to_select]
        if not fittest_cells:
            self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
        else:
            brains = [c.brain for c in fittest_cells]
            self.cells = self._create_new_population(brains)
    def _create_new_population(self, parent_brains):
        new_cells = []
        while len(new_cells) < JUMLAH_SEL_AWAL:
            p1, p2 = random.choices(parent_brains, k=2)
            child_brain = NeuralNetwork.crossover(p1, p2)
            child_brain.mutate(MUTATION_RATE, MUTATION_STRENGTH)
            new_cells.append(Cell(brain=child_brain))
        return new_cells

class SandboxMode(BaseSimulation):
    # ... (Kelas SandboxMode tidak ada perubahan) ...
    def __init__(self):
        super().__init__(title="Mode Sandbox")
        trained_brains = NeuralNetwork.load_brains(BRAIN_FILE)
        if not trained_brains:
            self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
        else:
            self.cells = [Cell(brain=random.choice(trained_brains)) for _ in range(JUMLAH_SEL_AWAL)]

def main():
    """Fungsi utama untuk menjalankan aplikasi dan menangani navigasi menu."""
    pygame.init()
    screen = pygame.display.set_mode((LEBAR_LAYAR, TINGGI_LAYAR))
    
    show_loading_screen(screen, "Memuat Dunia...")
    main_terrain = Terrain(LEBAR_LAYAR, TINGGI_LAYAR)

    app_running = True
    while app_running:
        main_menu = MainMenu(screen)
        main_choice = main_menu.run()

        game = None
        if main_choice == "train":
            training_menu = TrainingStartMenu(screen)
            training_choice = training_menu.run()
            if training_choice == "new_training":
                game = TrainingMode(start_from_scratch=True)
            elif training_choice == "continue_training":
                game = TrainingMode(start_from_scratch=False)
        elif main_choice == "sandbox":
            game = SandboxMode()
        elif main_choice == "world_menu":
            world_menu = WorldMenu(screen)
            world_choice = world_menu.run()
            if world_choice == "generate_world":
                show_loading_screen(screen, "Membuat Dunia Baru...")
                main_terrain = Terrain.create_new_world(LEBAR_LAYAR, TINGGI_LAYAR)
        elif main_choice in ("quit", "quit_app", "back"):
            app_running = False

        if game:
            game.terrain = main_terrain
            game.run()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()