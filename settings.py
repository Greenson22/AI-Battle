# settings.py

# --- PENGATURAN TAMPILAN ---
LEBAR_LAYAR, TINGGI_LAYAR = 800, 600
FRAME_RATE = 60

# Warna (R, G, B)
WARNA_LATAR = (10, 20, 40)
WARNA_SEL = (50, 255, 100)
WARNA_RUMPUT = (34, 139, 34)  # <-- Diubah dari WARNA_KRISTAL
WARNA_TEKS = (255, 255, 255)

# --- PENGATURAN SIMULASI & EVOLUSI ---
JUMLAH_SEL_AWAL = 40
JUMLAH_RUMPUT = 40
GENERATION_TIME_SECS = 15  # Detik per generasi
SELECTION_PERCENT = 0.25  # Persentase sel terbaik yang bertahan
MUTATION_RATE = 0.1  # 10% kemungkinan mutasi pada setiap bobot
MUTATION_STRENGTH = 0.1  # Seberapa kuat mutasinya
TURN_STRENGTH = 0.1  # Seberapa kuat sel berbelok

# --- PENGATURAN SEL & ENERGI ---
ENERGI_AWAL = 200
ENERGI_DIAM = 0.2  # Energi yang dikonsumsi meskipun diam
ENERGI_BERGERAK = 0.6  # Energi tambahan saat bergerak dengan kecepatan penuh
ENERGI_DARI_RUMPUT = 80  # <-- Diubah dari ENERGI_DARI_KRISTAL
ENERGI_TENGGELAM = 25
ENERGI_UNTUK_REPRODUKSI = 250  # Energi minimal untuk sel bertahan ke gen berikutnya
RADIUS_SEL = 7
RADIUS_RUMPUT = 5  # <-- Diubah dari RADIUS_KRISTAL
KECEPATAN_MAKS_SEL = 2
JARAK_DETEKSI_MAKANAN = 100 # Jarak dalam piksel di mana sel akan mulai 'foraging'

# --- PENGATURAN JARINGAN SARAF (ANN) ---
# Input: [jarak_rumput, sudut_rumput, energi_sendiri] # <-- Komentar diperbarui
NUM_INPUTS = 3
NUM_HIDDEN = 10
NUM_OUTPUTS = 7  # Output: [belok_kiri, belok_kanan, kecepatan]

# --- PENGATURAN TERRAIN ---
TERRAIN_SCALE = 1000.0
WARNA_TERRAIN = {
    'air': (40, 120, 180),
    'pasir': (240, 230, 140),
    'rumput': (34, 139, 34),
    'hutan': (0, 100, 0),
    'batu': (139, 137, 137)
}
# Level ketinggian untuk setiap biome (rentang 0.0 - 1.0)
TINGKAT_AIR = 0.3
TINGKAT_PASIR = 0.4
TINGKAT_RUMPUT = 0.6
TINGKAT_HUTAN = 0.8

# Pengaruh terrain terhadap kecepatan dan energi
PENGARUH_TERRAIN = {
    'air': {'speed_multiplier': 0.4, 'energy_cost': 1.5},
    'pasir': {'speed_multiplier': 0.7, 'energy_cost': 1.2},
    'rumput': {'speed_multiplier': 1.0, 'energy_cost': 1.0},
    'hutan': {'speed_multiplier': 0.8, 'energy_cost': 1.1},
    'batu': {'speed_multiplier': 0.6, 'energy_cost': 1.3},
}

# --- PENGATURAN SIMPAN & MUAT ---
BRAIN_FILE = 'data/fittest_brains.npz'
WORLD_FILE = 'data/world.npy'
WORLD_IMAGE_FILE = 'data/world.png'