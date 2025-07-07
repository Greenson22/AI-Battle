import pygame
from settings import WARNA_LATAR, WARNA_TEKS, LEBAR_LAYAR, TINGGI_LAYAR

def draw_gradient_background(screen):
    """Menggambar gradien vertikal untuk latar belakang yang lebih dinamis."""
    # Membuat warna atas sedikit lebih gelap dari warna latar utama
    top_color = tuple(max(0, c - 20) for c in WARNA_LATAR)
    bottom_color = WARNA_LATAR
    
    height = TINGGI_LAYAR
    for y in range(height):
        # Melakukan interpolasi linear antara dua warna
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (LEBAR_LAYAR, y))

def show_loading_screen(screen, text="Memuat..."):
    """Menampilkan layar pemuatan yang telah disempurnakan secara visual."""
    # Pengaturan font
    font_besar = pygame.font.Font(None, 80)
    font_kecil = pygame.font.Font(None, 30)

    # 1. Menggambar latar belakang dengan gradien
    draw_gradient_background(screen)
    
    # 2. Menggambar ikon sel yang lucu di bagian atas
    icon_center_x = LEBAR_LAYAR / 2
    icon_center_y = TINGGI_LAYAR / 2 - 120
    # Badan sel
    pygame.draw.circle(screen, (100, 200, 255), (icon_center_x, icon_center_y), 60)
    pygame.draw.circle(screen, (200, 240, 255), (icon_center_x, icon_center_y), 60, 4)
    # Mata
    eye_y = icon_center_y - 5
    pygame.draw.circle(screen, (255, 255, 255), (icon_center_x - 15, eye_y), 10)
    pygame.draw.circle(screen, (255, 255, 255), (icon_center_x + 15, eye_y), 10)
    pygame.draw.circle(screen, (0, 0, 0), (icon_center_x - 15, eye_y), 5)
    pygame.draw.circle(screen, (0, 0, 0), (icon_center_x + 15, eye_y), 5)

    # 3. Menampilkan teks pemuatan utama
    text_surf = font_besar.render(text, True, WARNA_TEKS)
    text_rect = text_surf.get_rect(center=(LEBAR_LAYAR / 2, TINGGI_LAYAR / 2 + 50))
    screen.blit(text_surf, text_rect)

    # 4. Menambahkan bingkai progress bar (statis)
    bar_width = 400
    bar_height = 30
    bar_x = (LEBAR_LAYAR - bar_width) / 2
    bar_y = TINGGI_LAYAR / 2 + 120
    pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height), 3, border_radius=15)
    
    # 5. Menambahkan teks "tips" atau sub-judul
    tip_text = "Membangun ekosistem..."
    tip_surf = font_kecil.render(tip_text, True, WARNA_TEKS)
    tip_rect = tip_surf.get_rect(center=(LEBAR_LAYAR / 2, bar_y + 60))
    screen.blit(tip_surf, tip_rect)

    # 6. Memperbarui tampilan di layar
    pygame.display.flip()