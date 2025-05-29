# blob.py
import random
import math
from settings import *
from utils import clamp, distance

class Blob:
    def __init__(self, x, y, speed, sense, size):
        self.x = x
        self.y = y
        self.speed = speed
        self.sense = sense
        self.size = size
        self.energy = ENERGY_PER_DAY
        self.food_eaten = 0
        self.angle = random.uniform(0, 2 * math.pi)

    def get_nearest_food(self, foods):
        min_dist = None
        nearest = None
        for food in foods:
            d = distance((self.x, self.y), (food.x, food.y))
            if d <= self.sense:
                if min_dist is None or d < min_dist:
                    min_dist = d
                    nearest = food
        return nearest

    def get_threat(self, blobs):
        for other in blobs:
            if other is self:
                continue
            if other.size > self.size * BLOB_EAT_BLOB_RATIO:
                d = distance((self.x, self.y), (other.x, other.y))
                if d <= self.sense:
                    return other
        return None

    def move(self, foods, blobs):
        threat = self.get_threat(blobs)
        if threat:
            dx = self.x - threat.x
            dy = self.y - threat.y
            self.angle = math.atan2(dy, dx)
        else:
            target = self.get_nearest_food(foods)
            if target:
                dx = target.x - self.x
                dy = target.y - self.y
                self.angle = math.atan2(dy, dx)
            else:
                if random.random() < 0.05:
                    self.angle = random.uniform(0, 2 * math.pi)
        dx = math.cos(self.angle) * self.speed
        dy = math.sin(self.angle) * self.speed
        r = BLOB_BASE_RADIUS * self.size
        self.x = clamp(self.x + dx, r, WIDTH - r)
        self.y = clamp(self.y + dy, r, HEIGHT - r)
        self.energy -= (self.size ** 3) * (self.speed ** 2)

    def eat(self):
        self.food_eaten += 1

    def is_alive(self):
        return self.food_eaten > 0

    def can_reproduce(self):
        return self.food_eaten >= 2

    def reproduce(self):
        new_speed = clamp(self.speed * (1 + random.uniform(-MUTATION_RATE, MUTATION_RATE)), SPEED_MIN, SPEED_MAX)
        new_sense = clamp(self.sense * (1 + random.uniform(-MUTATION_RATE, MUTATION_RATE)), SENSE_MIN, SENSE_MAX)
        new_size = clamp(self.size * (1 + random.uniform(-MUTATION_RATE, MUTATION_RATE)), SIZE_MIN, SIZE_MAX)
        return Blob(self.x, self.y, new_speed, new_sense, new_size)

    def get_color(self):
        t = (self.speed - SPEED_MIN) / (SPEED_MAX - SPEED_MIN)
        r = 255
        g = int(165 * t)
        b = int(255 * t)
        return (r, g, b)

    def get_radius(self):
        return int(BLOB_BASE_RADIUS * self.size) 