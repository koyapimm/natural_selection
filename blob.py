# blob.py
import random
import math
import uuid
from settings import *
from utils import clamp, distance
import matplotlib
import matplotlib.cm
import pygame

class Blob:
    def __init__(self, x, y, speed, sense, size, parent_id=None, generation=0):
        self.x = x
        self.y = y
        self.speed = speed
        self.sense = sense
        self.size = size
        self.energy = ENERGY_PER_DAY
        self.food_eaten = 0
        self.angle = random.uniform(0, 2 * math.pi)
        self.id = str(uuid.uuid4())  # Benzersiz kimlik
        self.parent_id = parent_id   # Ebeveyn kimliği (None ise ilk jenerasyon)
        self.generation = generation # Jenerasyon bilgisi
        self.alive = True
        self.fade_alpha = 255
        self.fade_radius = self.get_radius()
        self.last_reproduction_day = -REPRODUCTION_COOLDOWN_DAYS
        self.niche_bonus = False  # Niche bonusu aldı mı?
        self.age = 0  # Yaş (gün)
        self.efficiency = random.uniform(EFFICIENCY_MIN, EFFICIENCY_MAX)

    def get_nearest_food(self, foods):
        # Hızlı ve küçükler için bonus görüş
        bonus = 1.0
        if self.speed > 1.2:
            bonus += 0.15
        if self.size < 1.0:
            bonus += 0.10
        effective_sense = self.sense * bonus
        min_dist = None
        nearest = None
        for food in foods:
            d = distance((self.x, self.y), (food.x, food.y))
            if d <= effective_sense:
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

    def get_energy_cost(self):
        # Boyutun etkisi üstel, hızın etkisi yüksek, efficiency ile çarpılır
        return ENERGY_COST_COEFFICIENT * (self.size ** 2.1 + self.speed ** 1.3) * self.efficiency

    def move(self, foods, blobs, day=1):
        if not self.alive:
            return  # Ölü blob hareket etmesin
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
        # Enerji maliyeti
        energy_cost = self.get_energy_cost()
        self.energy -= energy_cost
        self.energy -= IDLE_ENERGY_COST  # Her frame idle maliyeti
        # Büyüklerin hızı sınırlandırılsın
        if self.size > 1.5:
            self.speed = min(self.speed, 0.8)
        # Küçükler daha hızlı olabilsin
        if self.size < 0.8:
            self.speed = max(self.speed, 0.7)

    def eat(self, food_type='food'):
        self.food_eaten += 1
        # Enerji artışı yemekle (küçükler için daha verimli)
        if food_type == 'food':
            self.energy += ENERGY_PER_DAY * BLOB_ENERGY_ON_EAT_FOOD / (self.size ** 0.65)
        elif food_type == 'blob':
            self.energy += ENERGY_PER_DAY * BLOB_ENERGY_ON_EAT_BLOB / (self.size ** 0.65)
        self.energy = clamp(self.energy, 0, self.get_max_energy())
        # Debug: Enerji ve yaşam durumu
        # print(f"Blob {self.id[:6]} eat: energy={self.energy}, alive={self.is_alive()}")

    def is_alive(self):
        return self.energy > 0

    def can_reproduce(self, current_day):
        threshold = REPRODUCTION_FOOD_THRESHOLD
        if self.size < 1.0:
            threshold = max(1, threshold - 1)
        if self.speed > 1.2:
            threshold = max(1, threshold - 1)
        enough_food = self.food_eaten >= threshold
        enough_energy = self.energy >= max(20, REPRODUCTION_ENERGY_FACTOR * self.size)
        cooldown_ok = (current_day - self.last_reproduction_day) >= REPRODUCTION_COOLDOWN_DAYS
        old_enough = self.age >= REPRODUCTION_MIN_AGE
        return enough_food and enough_energy and cooldown_ok and old_enough

    def reproduce(self, current_day):
        if random.random() < 0.4:
            new_speed = self.speed
            new_sense = self.sense
            new_size = self.size
            new_efficiency = self.efficiency
        else:
            new_speed = clamp(self.speed * (1 + random.uniform(-MUTATION_RATE, MUTATION_RATE)), SPEED_MIN, SPEED_MAX)
            new_sense = clamp(self.sense * (1 + random.uniform(-MUTATION_RATE, MUTATION_RATE)), SENSE_MIN, SENSE_MAX)
            new_size = clamp(self.size * (1 + random.uniform(-MUTATION_RATE, MUTATION_RATE)), SIZE_MIN, SIZE_MAX)
            new_efficiency = clamp(self.efficiency * (1 + random.uniform(-0.08, 0.08)), EFFICIENCY_MIN, EFFICIENCY_MAX)
            if random.random() < 0.10:
                trait = random.choice(['speed', 'sense', 'size', 'efficiency'])
                if trait == 'speed':
                    new_speed = clamp(new_speed * (1 + random.uniform(-0.35, 0.35)), SPEED_MIN, SPEED_MAX)
                elif trait == 'sense':
                    new_sense = clamp(new_sense * (1 + random.uniform(-0.35, 0.35)), SENSE_MIN, SENSE_MAX)
                elif trait == 'size':
                    new_size = clamp(new_size * (1 + random.uniform(-0.35, 0.35)), SIZE_MIN, SIZE_MAX)
                elif trait == 'efficiency':
                    new_efficiency = clamp(new_efficiency * (1 + random.uniform(-0.15, 0.15)), EFFICIENCY_MIN, EFFICIENCY_MAX)
        self.last_reproduction_day = current_day
        penalty = REPRODUCTION_ENERGY_PENALTY * (self.size ** 0.9)
        self.energy = int(self.energy * (1 - penalty))
        self.food_eaten = 0
        child_generation = self.generation + 1
        child_energy = ENERGY_PER_DAY
        if child_generation > MAX_GENERATION:
            child_energy = int(ENERGY_PER_DAY * 1.05)
        child = Blob(self.x, self.y, new_speed, new_sense, new_size, parent_id=self.id, generation=child_generation)
        child.efficiency = new_efficiency
        return child

    def get_color(self):
        """
        Jenerasyona göre renk döndürür. Viridis colormap kullanılır.
        """
        # Jenerasyonu normalize et (0-MAX_GENERATION arası)
        norm_gen = min(self.generation, MAX_GENERATION) / MAX_GENERATION
        cmap = matplotlib.cm.get_cmap("viridis")
        rgba = cmap(norm_gen)  # 0-1 arası RGBA
        rgb = tuple(int(255 * c) for c in rgba[:3])
        return rgb

    def get_radius(self):
        return int(BLOB_BASE_RADIUS * self.size)

    def get_max_energy(self):
        return get_max_energy(self.size)

    def update(self):
        if not self.alive:
            # Fade out and shrink
            self.fade_alpha = max(0, self.fade_alpha - 15)
            self.fade_radius = max(2, self.fade_radius - 1)
        # Enerjisi çok az olanlar hemen ölsün
        if self.alive and self.energy < 2:
            self.alive = False

    def draw(self, surface, show_vision=False, show_energy_halo=False, show_generation_label=False, font=None):
        pos = (int(self.x), int(self.y))
        radius = self.fade_radius if not self.is_alive() else self.get_radius()
        color = self.get_color()
        # Vision range
        if show_vision:
            vision_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(vision_surf, (100, 200, 255, 40), pos, int(self.sense), 0)
            surface.blit(vision_surf, (0, 0))
        # Energy halo
        if show_energy_halo and self.energy > ENERGY_PER_DAY * 0.8 and self.is_alive():
            pygame.draw.circle(surface, (255, 255, 180), pos, radius + 4, 2)
        # Blob itself (with fade if dead)
        if not self.is_alive():
            fade_color = (*color, self.fade_alpha)
            blob_surf = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(blob_surf, fade_color, (radius + 1, radius + 1), radius)
            surface.blit(blob_surf, (pos[0] - radius - 1, pos[1] - radius - 1))
        else:
            pygame.draw.circle(surface, color, pos, radius)
        # Generation label
        if show_generation_label and font is not None:
            gen_text = font.render(str(self.generation), True, (255, 255, 255))
            surface.blit(gen_text, (pos[0] - radius, pos[1] - radius - 10)) 