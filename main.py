# main.py

import pygame
import sys
import os # <-- Tambahkan import ini

# vvv TAMBAHKAN BLOK KODE INI vvv
# Menambahkan direktori root proyek ke path Python
# Ini memastikan semua impor 'from src...' berfungsi dengan benar
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# ^^^ TAMBAHKAN BLOK KODE INI ^^^

from settings import LEBAR_LAYAR, TINGGI_LAYAR
from terrain import Terrain

# Import dari struktur folder baru
from src.ui.menus import MainMenu, TrainingStartMenu, WorldMenu
from src.simulation.modes import TrainingMode, SandboxMode
from src.utils.helpers import show_loading_screen

# ... sisa kode main.py tidak ada yang berubah ...
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