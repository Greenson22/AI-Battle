# src/utils/helpers.py

import pygame
from settings import WARNA_LATAR, WARNA_TEKS, LEBAR_LAYAR, TINGGI_LAYAR

def show_loading_screen(screen, text="Memuat..."):
    """Menampilkan layar pemuatan sederhana."""
    font_loading = pygame.font.Font(None, 74)
    screen.fill(WARNA_LATAR)
    text_surf = font_loading.render(text, True, WARNA_TEKS)
    text_rect = text_surf.get_rect(center=(LEBAR_LAYAR / 2, TINGGI_LAYAR / 2))
    screen.blit(text_surf, text_rect)
    pygame.display.flip()