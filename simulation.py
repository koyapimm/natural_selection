# simulation.py
import random
from settings import *
from blob import Blob
from food import Food
from utils import distance

def spawn_food():
    return [Food(random.uniform(FOOD_RADIUS, WIDTH - FOOD_RADIUS),
                 random.uniform(FOOD_RADIUS, HEIGHT - FOOD_RADIUS))
            for _ in range(FOOD_PER_DAY)]

def spawn_initial_blobs():
    return [Blob(random.uniform(BLOB_BASE_RADIUS, WIDTH - BLOB_BASE_RADIUS),
                 random.uniform(BLOB_BASE_RADIUS, HEIGHT - BLOB_BASE_RADIUS),
                 random.uniform(SPEED_MIN, SPEED_MAX),
                 random.uniform(SENSE_MIN, SENSE_MAX),
                 random.uniform(SIZE_MIN, SIZE_MAX))
            for _ in range(INITIAL_BLOBS)]

def handle_eating(blobs, foods):
    # Bloblar birbirini yiyebilir mi?
    eaten_blobs = set()
    for predator in blobs:
        for prey in blobs:
            if predator is prey or prey in eaten_blobs:
                continue
            if predator.size > prey.size * BLOB_EAT_BLOB_RATIO:
                d = distance((predator.x, predator.y), (prey.x, prey.y))
                if d < predator.get_radius() + prey.get_radius():
                    predator.eat()
                    predator.energy += ENERGY_PER_DAY * BLOB_ENERGY_ON_EAT_BLOB
                    eaten_blobs.add(prey)
    for prey in eaten_blobs:
        if prey in blobs:
            blobs.remove(prey)
    # Yemek yeme
    for blob in blobs:
        for food in foods[:]:
            if distance((blob.x, blob.y), (food.x, food.y)) < blob.get_radius() + FOOD_RADIUS:
                blob.eat()
                foods.remove(food)
                break

def next_generation(blobs):
    new_blobs = []
    for blob in blobs:
        if blob.is_alive():
            blob.energy = ENERGY_PER_DAY
            num_children = blob.food_eaten // 2  # 2+ yemek → çocuk
            new_blobs.append(blob)
            for _ in range(num_children):
                child = blob.reproduce()
                new_blobs.append(child)
            blob.food_eaten = 0
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