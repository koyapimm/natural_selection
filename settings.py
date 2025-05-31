# settings.py
"""
Simülasyon ve görselleştirme için sabitler ve parametreler.
"""

# Ekran ve görsel ayarlar
WIDTH = 800
HEIGHT = 600
FPS = 60
BG_COLOR = (30, 30, 30)
BLOB_BASE_RADIUS = 10
FOOD_RADIUS = 4
FOOD_COLOR = (255, 220, 0)
DAY_LENGTH = 6  # saniye

# Simülasyon parametreleri
INITIAL_BLOBS = 50
BASE_FOOD_COUNT = 95
FOOD_PER_DAY = BASE_FOOD_COUNT
BASE_ENERGY = 150
ENERGY_PER_DAY = BASE_ENERGY
MAX_ENERGY = 200
ENERGY_COST_COEFFICIENT = 0.18
SPEED_MIN = 0.5
SPEED_MAX = 1.5
SENSE_MIN = 30
SENSE_MAX = 120
SIZE_MIN = 0.5
SIZE_MAX = 2.0

# Mutasyon oranı (adaptif için taban ve maksimum)
BASE_MUTATION_RATE = 0.08
MAX_MUTATION_RATE = 0.25
DIVERSITY_THRESHOLD = 0.04  # Çeşitlilik bu değerin altına inerse mutasyon artar
MUTATION_RATE = BASE_MUTATION_RATE

# Evrimsel kurallar
BLOB_EAT_BLOB_RATIO = 1.2  # %20 büyükse yiyebilir
BLOB_ENERGY_ON_EAT_BLOB = 1.0  # başka blob yerse %100 enerji kazanır
BLOB_ENERGY_ON_EAT_FOOD = 0.8  # yemek yerse %80 enerji kazanır
MAX_GENERATION = 20  # Jenerasyon renk skalası için üst sınır
REPRODUCTION_FOOD_THRESHOLD = 3  # 3 yemek = 1 çocuk
REPRODUCTION_MIN_ENERGY = int(ENERGY_PER_DAY * 1.0)
REPRODUCTION_ENERGY_PENALTY = 0.3  # Üreme sonrası enerji kaybı %
REPRODUCTION_COOLDOWN_DAYS = 2  # Üreme sonrası bekleme süresi (gün)
EARLY_FOOD_MULTIPLIER = 2.0
EARLY_FOOD_DAYS = 3
IDLE_ENERGY_COST = 0.03
REPRODUCTION_MIN_AGE = 2  # Üreme için minimum yaş (gün)
EFFICIENCY_MIN = 0.8
EFFICIENCY_MAX = 1.2
REPRODUCTION_ENERGY_FACTOR = 30  # Üreme için gereken enerji = 30 * size

# Enerji depolama kapasitesi (boyuta göre)
def get_max_energy(size):
    return int(120 + 80 * (size ** 1.2))  # Küçükler için düşük, büyükler için yüksek

NICHE_BONUS = 0.12  # Nadir özellikli bireylere günlük enerji bonusu oranı

# --- Statistics/Logging Toggles ---
ENABLE_STATS = True
STATS_PLOT_INTERVAL = 10  # days
STATS_SAVE_PNG = True
STATS_SAVE_CSV = True
STATS_OUTPUT_DIR = "stats_output"

# ... existing code ... 