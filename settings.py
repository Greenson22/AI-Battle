# settings.py

# --- PENGATURAN TAMPILAN ---
LEBAR_LAYAR, TINGGI_LAYAR = 800, 600
FRAME_RATE = 60

# Warna (R, G, B)
WARNA_LATAR = (10, 20, 40)
WARNA_SEL = (50, 255, 100)
WARNA_RUMPUT = (34, 139, 34)
WARNA_TEKS = (255, 255, 255)

# --- PENGATURAN SIMULASI & EVOLUSI ---
JUMLAH_SEL_AWAL = 1
JUMLAH_RUMPUT = 40
GENERATION_TIME_SECS = 15
SELECTION_PERCENT = 0.25
MUTATION_RATE = 0.1
MUTATION_STRENGTH = 0.1
TURN_STRENGTH = 0.1

# --- PENGATURAN SEL & ENERGI ---
ENERGI_AWAL = 200
ENERGI_DIAM = 0.2
ENERGI_BERGERAK = 0.6
ENERGI_DARI_RUMPUT = 80
ENERGI_TENGGELAM = 25
ENERGI_UNTUK_REPRODUKSI = 250
RADIUS_SEL = 7
RADIUS_RUMPUT = 5
KECEPATAN_MAKS_SEL = 2
JARAK_DETEKSI_MAKANAN = 100

# --- Pengaturan Fitness & Perilaku ---
JARAK_DETEKSI_SOSIAL = 75
BONUS_FITNESS_MAKAN = 50
BONUS_FITNESS_SOSIAL = 5

# --- PENGATURAN PENGLIHATAN SEL (BARU) ---
JARAK_PENGLIHATAN_SEL = 50  # Jarak (radius) sensor dari pusat sel
JUMLAH_SENSOR_TERRAIN = 8  # Jumlah "mata" di sekitar sel

# --- PENGATURAN JARINGAN SARAF (ANN) ---
# Input: [jarak_rumput, sudut_rumput, energi_sendiri, sensor_terrain_1, ..., sensor_terrain_8]
NUM_INPUTS = 3 + JUMLAH_SENSOR_TERRAIN  # <-- JUMLAH INPUT DIPERBARUI
NUM_HIDDEN = 10
NUM_OUTPUTS = 7 # Output tetap sama

# --- PENGATURAN TERRAIN ---
TERRAIN_SCALE = 1000.0
WARNA_TERRAIN = {
    'air': (40, 120, 180),
    'pasir': (240, 230, 140),
    'rumput': (34, 139, 34),
    'hutan': (0, 100, 0),
    'batu': (139, 137, 137)
}
# Level ketinggian untuk setiap biome
TINGKAT_AIR = 0.3
TINGKAT_PASIR = 0.4
TINGKAT_RUMPUT = 0.6
TINGKAT_HUTAN = 0.8

# Pengaruh terrain terhadap sel
PENGARUH_TERRAIN = {
    'air': {'speed_multiplier': 0.4, 'energy_cost': 1.5},
    'pasir': {'speed_multiplier': 0.7, 'energy_cost': 1.2},
    'rumput': {'speed_multiplier': 1.0, 'energy_cost': 1.0},
    'hutan': {'speed_multiplier': 0.8, 'energy_cost': 1.1},
    'batu': {'speed_multiplier': 0.6, 'energy_cost': 1.3},
}

# Nilai numerik untuk input sensor (BARU)
NILAI_SENSOR_TERRAIN = {
    'air': -1.0,
    'pasir': -0.5,
    'rumput': 0.5,
    'hutan': 0.2,
    'batu': -0.7
}

# --- PENGATURAN SIMPAN & MUAT ---
BRAIN_FILE = 'data/fittest_brains.npz'
WORLD_FILE = 'data/world.npy'
WORLD_IMAGE_FILE = 'data/world.png'