# settings.py

# --- PENGATURAN TAMPILAN ---
LEBAR_LAYAR, TINGGI_LAYAR = 800, 600
FRAME_RATE = 60

# Warna (R, G, B)
WARNA_LATAR = (10, 20, 40)
WARNA_SEL = (50, 255, 100)
WARNA_KRISTAL = (255, 200, 50)
WARNA_TEKS = (255, 255, 255)

# --- PENGATURAN SIMULASI & EVOLUSI ---
JUMLAH_SEL_AWAL = 50
JUMLAH_KRISTAL = 30
GENERATION_TIME_SECS = 15 # Detik per generasi
SELECTION_PERCENT = 0.25  # Persentase sel terbaik yang bertahan
MUTATION_RATE = 0.1       # 10% kemungkinan mutasi pada setiap bobot
MUTATION_STRENGTH = 0.1   # Seberapa kuat mutasinya

# --- PENGATURAN SEL & ENERGI ---
ENERGI_AWAL = 200
ENERGI_DIAM = 0.2 # Energi yang dikonsumsi meskipun diam
ENERGI_BERGERAK = 0.6 # Energi tambahan saat bergerak dengan kecepatan penuh
ENERGI_DARI_KRISTAL = 100
ENERGI_UNTUK_REPRODUKSI = 250 # Energi minimal untuk sel bertahan ke gen berikutnya
RADIUS_SEL = 7
RADIUS_KRISTAL = 5
KECEPATAN_MAKS_SEL = 2 

# --- PENGATURAN JARINGAN SARAF (ANN) ---
# Input: [jarak_kristal, sudut_kristal, energi_sendiri]
NUM_INPUTS = 3
NUM_HIDDEN = 10
NUM_OUTPUTS = 3 # Output: [belok_kiri, belok_kanan, kecepatan]