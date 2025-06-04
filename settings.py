# settings.py
# Proje genelinde kullanılacak tüm sabitler burada tanımlanır.
# Diğer modüller bu dosyadan veri çeker.

# --- Ekran ve Görsel Ayarlar ---
SCREEN_WIDTH = 1200           # Simülasyon penceresinin genişliği (piksel)
SCREEN_HEIGHT = 900          # Simülasyon penceresinin yüksekliği (piksel)
FPS = 60                     # Saniyedeki kare (frame) sayısı

# --- Renkler (RGB) ---
COLOR_BACKGROUND = (30, 30, 40)   # Arkaplan rengi
COLOR_BLOB = (0, 200, 255)        # Blob'ların varsayılan rengi
COLOR_FOOD = (80, 220, 60)        # Yiyeceklerin rengi

# --- Simülasyon Başlangıç Parametreleri ---
INITIAL_BLOB_COUNT = 100      # Simülasyon başlangıcındaki blob sayısı
INITIAL_FOOD_COUNT = 100      # Simülasyon başlangıcındaki yiyecek sayısı

# --- Enerji ve Yaşam Parametreleri ---
BLOB_INITIAL_ENERGY = 100    # Bir blob'un başlangıç enerjisi
BLOB_MAX_ENERGY = 200        # Bir blob'un sahip olabileceği maksimum enerji
ENERGY_PER_FOOD = 40         # Bir yiyecekten alınan enerji miktarı
EFFICIENCY_NON_PREF_FOOD = 0.25   # Blob kendi preferred_food dışındaki yiyecekten bu oranda enerji alır

# --- Mutasyon ve Evrim Parametreleri ---
MUTATION_RATE = 0.05         # Üreme sırasında mutasyon olasılığı
MUTATION_STRENGTH = 0.1      # Mutasyonun genetik özelliklere etkisi (oran)

# --- Diğer Sabitler ---
BLOB_RADIUS = 8              # Blob'ların ekranda çizilen yarıçapı (piksel)
FOOD_RADIUS = 4              # Yiyeceklerin ekranda çizilen yarıçapı (piksel)

# --- Üreme Parametreleri ---
REPRODUCTION_COST = 40  # Bir blob'un üremek için harcaması gereken enerji miktarı

# --- Kaynak Yenilenme ---
FOOD_RESPAWN_INTERVAL = 100    # Her 100 frame'de bir
FOOD_RESPAWN_AMOUNT = 40        # 40 yeni food eklenir

# --- Görsel Ayar Toggles ---
SHOW_VISION = False             # Blob'ların görüş alanı çizilsin mi?
SHOW_ENERGY_ALPHA = False       # Enerjiye göre blob rengi soluklaşsın mı? (eski)
SHOW_ENERGY_CIRCLE = False      # Enerjiye göre dış halka çizilsin mi?
SHOW_METABOLISM_COLOR = False   # Metabolizma tipine göre renk kullanılsın mı?
SHOW_ENERGY_GLOW = False        # Enerjisi yüksek blob'larda parlak bir aura gösterilsin mi?
SHOW_NEWBORN_GLOW = False      # Yeni doğan blob'lar özel efektle vurgulansın mı?
SHOW_ROTTEN_FOOD = False       # Çürümüş yiyecekler haritada soluk/koyu gösterilsin mi?

# --- Yeni Sabitler ---
FRAMES_PER_DAY = 300         # Bir gün kaç frame sürer
FOOD_LIFESPAN = 1000         # Bir yiyecek maksimum kaç frame hayatta kalır

# --- Yiyecek Türleri ve Renkleri ---
FOOD_TYPES = ["green", "red", "blue"]
FOOD_TYPE_COLORS = {
    "green": (80, 220, 60),
    "red": (220, 80, 60),
    "blue": (60, 120, 220)
}

# --- Genetik Özellik Sınırları ---
SPEED_MIN = 0.5
SPEED_MAX = 3.0
SIZE_MIN = 5
SIZE_MAX = 12
VISION_MIN = 40
VISION_MAX = 150

ENERGY_LOSS_PER_STEP = 0.2   # Her adımda kaybedilen enerji miktarı

# --- Yeni Sabitler ---
BLOB_ENERGY_GAIN_ON_HUNT = 40  # Avlanan blob başına kazanılan enerji miktarı

# --- Aggression Görsel Sabitleri ---
AGGRESSION_COLOR_LOW = (80, 200, 255)    # Düşük aggression (mavi)
AGGRESSION_COLOR_HIGH = (255, 60, 60)    # Yüksek aggression (kırmızı)
SHOW_AGGRESSION_AURA = True              # Aggression'a göre aura gösterilsin mi?
SHOW_HUNT_LINES = True                   # Avcı/korkan çizgiler gösterilsin mi?

# --- Gün Döngüsü (Day-Night Cycle) ---
DAY_COLOR = (30, 30, 40)      # Gündüz arkaplan rengi
NIGHT_COLOR = (10, 10, 30)    # Gece arkaplan rengi
DAY_NIGHT_CYCLE = True        # Gün döngüsü aktif mi?

# --- Aggression Mutasyon Ayarı ---
AGGRESSION_MUTATION_RATE = 0.02  # Aggression geninin mutasyon olasılığı (default: %2)

# --- Metabolizma Davranış Parametreleri ---
DAY_METABOLISM_SPEED_FACTOR = 1.0      # Gündüz, 'day' metabolizmalı blob'lar için hız çarpanı
DAY_METABOLISM_ENERGY_FACTOR = 1.0     # Gündüz, 'day' metabolizmalı blob'lar için enerji kaybı çarpanı
NIGHT_METABOLISM_SPEED_FACTOR = 0.5    # Gece, 'day' metabolizmalı blob'lar için hız çarpanı
NIGHT_METABOLISM_ENERGY_FACTOR = 1.5   # Gece, 'day' metabolizmalı blob'lar için enerji kaybı çarpanı

NIGHT_BONUS_SPEED_FACTOR = 1.0         # Gece, 'night' metabolizmalı blob'lar için hız çarpanı
NIGHT_BONUS_ENERGY_FACTOR = 1.0        # Gece, 'night' metabolizmalı blob'lar için enerji kaybı çarpanı
DAY_BONUS_SPEED_FACTOR = 0.5           # Gündüz, 'night' metabolizmalı blob'lar için hız çarpanı
DAY_BONUS_ENERGY_FACTOR = 1.5          # Gündüz, 'night' metabolizmalı blob'lar için enerji kaybı çarpanı

NEUTRAL_SPEED_FACTOR = 1.0             # 'neutral' metabolizmalı blob'lar için hız çarpanı
NEUTRAL_ENERGY_FACTOR = 1.0            # 'neutral' metabolizmalı blob'lar için enerji kaybı çarpanı

# Gerekirse yeni sabitler buraya eklenebilir.
PAUSE_SIMULATION = False
SIMULATION_SPEED = FPS
SIMULATION_SPEED_MIN = 10
SIMULATION_SPEED_MAX = 240

# --- Yeni Sabitler ---
AGGRESSION_THRESHOLD = 0.6
BASE_SPEED_COST = 0.002
BASE_SIZE_COST = 0.003
BASE_VISION_COST = 0.0005
SIZE_MARGIN = 0.85  # Avcı, kendinden bu oranda küçükleri avlayabilir
HUNT_ENERGY_GAIN_RATIO = 0.5  # Avcı, avın enerjisinin %50'sini alır
ESCAPE_SIZE_RATIO = 0.7  # Kaçan, tehditten bu oranda küçükse kaçar
ESCAPE_AGGRESSION_THRESHOLD = 0.3  # Kaçan için aggression eşiği
FOOD_ENERGY_GREEN = 1.0
FOOD_ENERGY_RED = 4.0
FOOD_ENERGY_BLUE = 2.5
SIZE_SPEED_TRADEOFF = 0.15  # Size artarsa speed bu oranda azalır
EFF_AGGR_TRADEOFF = 0.2     # Efficiency artarsa aggression bu oranda azalır
VISION_SPEED_TRADEOFF = 0.1 # Vision artarsa speed bu oranda azalır

# --- Yeni Sabitler ---
BASE_THRESHOLD = 12.0
SIZE_FACTOR = 1.2
POP_OVERLOAD_LIMIT = 300
POP_OVERLOAD_MULTIPLIER = 0.002
MIN_ENERGY_THRESHOLD = 1.0
AGE_LIMIT = 2000

# --- Biome/Zone Constants ---
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 800

ZONE_A = (0, 0, 400, 400)      # Top-Left
ZONE_B = (800, 0, 400, 400)    # Top-Right
ZONE_C = (0, 400, 400, 400)    # Bottom-Left
ZONE_D = (800, 400, 400, 400)  # Bottom-Right
ZONE_E = (400, 200, 400, 400)  # Center Hot Zone

# --- Species Parameters ---
SPECIES = {
    'herbivore': {
        'food_weights': {'green': 0.8, 'red': 0.1, 'blue': 0.1},
        'metabolism_bias': 'day',
        'aggression_range': (0.0, 0.3),
        'max_population': 50,
        'energy_cost_multiplier': 1.0,
    },
    'omnivore': {
        'food_weights': {'green': 0.33, 'red': 0.33, 'blue': 0.34},
        'metabolism_bias': 'neutral',
        'aggression_range': (0.3, 0.6),
        'max_population': 50,
        'energy_cost_multiplier': 1.1,
    },
    'predator': {
        'food_weights': {'green': 0.1, 'red': 0.1, 'blue': 0.8},
        'metabolism_bias': 'night',
        'aggression_range': (0.6, 1.0),
        'max_population': 50,
        'energy_cost_multiplier': 1.2,
    },
    'hybrid': {
        'food_weights': {'green': 0.3, 'red': 0.4, 'blue': 0.3},
        'metabolism_bias': 'neutral',
        'aggression_range': (0.2, 0.8),
        'max_population': 50,
        'energy_cost_multiplier': 1.05,
    },
}

# --- Central Zone (E) Risk/Reward ---
ZONE_E_FOOD_MULTIPLIER = 2.0  # Food spawns at double rate
ZONE_E_ENTRY_PENALTY = 5.0    # Flat energy cost to enter
ZONE_E_RANDOM_EVENT_CHANCE = 0.15  # 15% chance per frame for random effect
ZONE_E_RANDOM_EFFECTS = ['stun', 'random_move', 'aggression_spike']