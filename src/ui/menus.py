# src/ui/menus.py

import pygame
from settings import WARNA_LATAR, WARNA_TEKS, LEBAR_LAYAR
from src.ui.button import Button # Import dari file button

class BaseMenu:
    """Kelas dasar untuk semua menu dalam aplikasi."""
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
    """Menu utama aplikasi."""
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
    """Sub-menu untuk memilih mode latihan."""
    def __init__(self, screen):
        super().__init__(screen, "Mode Latihan")
        btn_width, btn_height = 400, 60
        btn_x = (LEBAR_LAYAR - btn_width) / 2
        self.buttons = {
            "new_training": Button(btn_x, 200, btn_width, btn_height, "Mulai dari Awal", (20, 140, 180), (30, 160, 200)),
            "continue_training": Button(btn_x, 280, btn_width, btn_height, "Lanjutkan dari File", (20, 180, 140), (30, 200, 160)),
        }

class WorldMenu(BaseMenu):
    """Menu untuk mengelola dunia/terrain."""
    def __init__(self, screen):
        super().__init__(screen, "Pengaturan Dunia")
        btn_width, btn_height = 450, 60
        btn_x = (LEBAR_LAYAR - btn_width) / 2
        self.buttons = {
            "generate_world": Button(btn_x, 200, btn_width, btn_height, "Buat & Simpan Dunia Baru", (20, 140, 180), (30, 160, 200)),
            "back": Button(btn_x, 280, btn_width, btn_height, "Kembali", (100, 100, 100), (150, 150, 150)),
        }