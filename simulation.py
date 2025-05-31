# simulation.py
import random
import json
import os
import numpy as np
from settings import *
from blob import Blob
from food import Food
from utils import distance
from utils import clamp

def spawn_food(food_count=None):
    if food_count is None:
        food_count = FOOD_PER_DAY
    foods = []
    for _ in range(food_count):
        if random.random() < 0.2:
            # Küçük kümeler oluştur
            cx = random.uniform(FOOD_RADIUS, WIDTH - FOOD_RADIUS)
            cy = random.uniform(FOOD_RADIUS, HEIGHT - FOOD_RADIUS)
            for _ in range(random.randint(2, 4)):
                fx = min(max(cx + random.gauss(0, 20), FOOD_RADIUS), WIDTH - FOOD_RADIUS)
                fy = min(max(cy + random.gauss(0, 20), FOOD_RADIUS), HEIGHT - FOOD_RADIUS)
                foods.append(Food(fx, fy))
        else:
            foods.append(Food(random.uniform(FOOD_RADIUS, WIDTH - FOOD_RADIUS),
                              random.uniform(FOOD_RADIUS, HEIGHT - FOOD_RADIUS)))
    return foods[:food_count]

def spawn_initial_blobs():
    return [Blob(random.uniform(BLOB_BASE_RADIUS, WIDTH - BLOB_BASE_RADIUS),
                 random.uniform(BLOB_BASE_RADIUS, HEIGHT - BLOB_BASE_RADIUS),
                 random.uniform(SPEED_MIN, SPEED_MAX),
                 random.uniform(SENSE_MIN, SENSE_MAX),
                 random.uniform(SIZE_MIN, SIZE_MAX),
                 parent_id=None, generation=0)
            for _ in range(INITIAL_BLOBS)]

def apply_niche_bonus(blobs):
    # Özelliklerin dağılımını bul
    speeds = [b.speed for b in blobs]
    sizes = [b.size for b in blobs]
    senses = [b.sense for b in blobs]
    # Nadirlik için alt ve üst %20'lik dilimi bul
    speed_low, speed_high = np.percentile(speeds, 20), np.percentile(speeds, 80)
    size_low, size_high = np.percentile(sizes, 20), np.percentile(sizes, 80)
    sense_low, sense_high = np.percentile(senses, 20), np.percentile(senses, 80)
    for b in blobs:
        b.niche_bonus = False
        if (b.speed < speed_low or b.speed > speed_high or
            b.size < size_low or b.size > size_high or
            b.sense < sense_low or b.sense > sense_high):
            b.energy += int(ENERGY_PER_DAY * NICHE_BONUS)
            b.energy = clamp(b.energy, 0, b.get_max_energy())
            b.niche_bonus = True

def handle_eating(blobs, foods):
    # 1. Bloblar birbirini yiyebilir mi? (sadece işaretle, silme yok)
    eaten_blobs = set()
    blob_eat_events = []
    for predator in blobs[:]:
        for prey in blobs[:]:
            if predator is prey or prey in eaten_blobs:
                continue
            if predator.size > prey.size * BLOB_EAT_BLOB_RATIO:
                d = distance((predator.x, predator.y), (prey.x, prey.y))
                if d < predator.get_radius() + prey.get_radius():
                    blob_eat_events.append((predator, prey))
                    eaten_blobs.add(prey)
    # 2. Tüm blob yeme işlemlerini uygula (enerji artışı)
    for predator, prey in blob_eat_events:
        predator.eat('blob')
    # 3. Yemeği ilk ulaşan blob alır
    foods_left = foods[:]
    food_eat_events = []
    for food in foods_left[:]:
        candidates = [b for b in blobs if distance((b.x, b.y), (food.x, food.y)) < b.get_radius() + FOOD_RADIUS]
        if candidates:
            nearest = min(candidates, key=lambda b: distance((b.x, b.y), (food.x, food.y)))
            food_eat_events.append((nearest, food))
            foods_left.remove(food)
    # 4. Tüm food yeme işlemlerini uygula (enerji artışı)
    for blob, food in food_eat_events:
        blob.eat('food')
        if food in foods:
            foods.remove(food)
    # 5. Tüm prey'leri döngüden sonra sil
    for prey in eaten_blobs:
        if prey in blobs:
            blobs.remove(prey)

def next_generation(blobs, day):
    new_blobs = []
    for blob in blobs:
        if blob.is_alive():
            if blob.can_reproduce(day):
                child = blob.reproduce(day)
                new_blobs.append(child)
            new_blobs.append(blob)
    return new_blobs

def average_speed(blobs):
    if not blobs:
        return 0
    return sum(b.speed for b in blobs) / len(blobs)

def average_sense(blobs):
    if not blobs:
        return 0
    return sum(b.sense for b in blobs) / len(blobs)

def average_size(blobs):
    if not blobs:
        return 0
    return sum(b.size for b in blobs) / len(blobs)

def save_genealogy(day, blobs, filename="genealogy.json"):
    """
    Her gün sonunda jenerasyon başına hayatta kalan birey sayısını genealogy.json dosyasına kaydeder.
    """
    # Dosya varsa oku, yoksa boş başlat
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    # Jenerasyon sayımı
    gen_counts = {}
    for blob in blobs:
        gen_key = f"jenerasyon_{blob.generation}"
        gen_counts[gen_key] = gen_counts.get(gen_key, 0) + 1
    data[f"Gün {day}"] = gen_counts
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def increment_blob_ages(blobs):
    for b in blobs:
        b.age += 1 