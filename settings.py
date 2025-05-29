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

# Simülasyon parametreleri
INITIAL_BLOBS = 50
FOOD_PER_DAY = 80
ENERGY_PER_DAY = 100
SPEED_MIN = 0.5
SPEED_MAX = 1.5
SENSE_MIN = 30
SENSE_MAX = 120
SIZE_MIN = 0.5
SIZE_MAX = 2.0
MUTATION_RATE = 0.05
DAY_LENGTH = 4  # saniye

# Evrimsel kurallar
BLOB_EAT_BLOB_RATIO = 1.2  # %20 büyükse yiyebilir
BLOB_ENERGY_ON_EAT_BLOB = 0.5  # başka blob yerse %50 enerji kazanır 