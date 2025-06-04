"""
blob.py
Evrimsel yapay yaşam simülasyonunda bir canlıyı (Blob) temsil eden sınıf.
Genetik özellikler, enerji ve temel davranışlar içerir.
"""

import random
import pygame
import math
import settings
from settings import (
    BLOB_INITIAL_ENERGY, BLOB_RADIUS, SCREEN_WIDTH, SCREEN_HEIGHT,
    SHOW_VISION, SHOW_ENERGY_ALPHA, SHOW_ENERGY_CIRCLE, SHOW_METABOLISM_COLOR, SHOW_ENERGY_GLOW, SHOW_NEWBORN_GLOW,
    SHOW_AGGRESSION_AURA, AGGRESSION_COLOR_LOW, AGGRESSION_COLOR_HIGH
)

# Metabolizma tipleri
METABOLISM_TYPES = ["day", "night", "neutral"]

# Metabolizma tipine göre renk kodlaması
COLOR_MAP = {
    "day": (255, 255, 100),
    "night": (100, 100, 255),
    "neutral": (180, 255, 180)
}
ENERGY_COLOR = (255, 120, 40)  # Enerji halkası için renk
NEWBORN_COLOR = (255, 255, 255)  # Yeni doğan efekt rengi (beyaz parıltı)

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))

def generate_random_dna(preferred_food=None, initial=False, aggression=None):
    """
    Rastgele DNA üretir. initial=True ise efficiency [1.0,1.1], vision ortalamaya yakın başlatılır.
    aggression parametresi verilirse onu kullanır.
    Başlangıç popülasyonunda %15-20 yüksek aggression, geri kalanı düşük aggression olacak şekilde dağıtılır.
    """
    if initial:
        efficiency = random.uniform(1.0, 1.1)
        vision = random.uniform(90, 110)
        # Controlled aggression distribution for initial population
        if aggression is not None:
            aggr = aggression
        else:
            aggr = random.uniform(0.7, 1.0) if random.random() < 0.18 else random.uniform(0.0, 0.45)
    else:
        efficiency = random.uniform(0.9, 1.1)
        vision = random.uniform(settings.VISION_MIN, settings.VISION_MAX)
        aggr = aggression if aggression is not None else random.uniform(0.0, 1.0)
    return {
        "speed": random.uniform(settings.SPEED_MIN, settings.SPEED_MAX),
        "size": random.uniform(settings.SIZE_MIN, settings.SIZE_MAX),
        "vision": vision,
        "efficiency": efficiency,
        "metabolism": random.choice(METABOLISM_TYPES),
        "preferred_food": preferred_food if preferred_food is not None else random.choice(settings.FOOD_TYPES),
        "aggression": aggr
    }

class Blob:
    def __init__(self, x=None, y=None, dna=None, energy=None, is_newborn=False, newborn_max_age=40, initial=False, species=None):
        """
        Yeni bir blob oluşturur: rastgele konum, enerji ve DNA ile başlar.
        """
        self.species = species
        self.x = x if x is not None else random.uniform(settings.BLOB_RADIUS, settings.SCREEN_WIDTH - settings.BLOB_RADIUS)
        self.y = y if y is not None else random.uniform(settings.BLOB_RADIUS, settings.SCREEN_HEIGHT - settings.BLOB_RADIUS)
        self.energy = energy if energy is not None else settings.BLOB_INITIAL_ENERGY
        self.dna = dna if dna is not None else generate_random_dna(initial=initial)
        self.target = None  # Hedef food nesnesi
        # Yeni doğan efektleri
        self.is_newborn = is_newborn
        self.newborn_age = 0
        self.newborn_max_age = newborn_max_age  # Kaç frame boyunca yeni doğan sayılacak
        self.fade_alpha = 255  # Fade out için
        self.hunt_target = None  # Avcılık çizgisi için hedef blob
        self.flee_target = None  # Kaçma çizgisi için tehdit blob
        self.wander_target = None  # Hedefsiz dolaşma için rastgele hedef
        self.hunt_cooldown = 0  # Avlanma cooldown'u
        # Genetikten renk hesaplama
        min_speed, max_speed = 0.5, 5.0
        min_size, max_size = 5, 20
        min_vision, max_vision = 20, 120
        speed = self.dna["speed"]
        size = self.dna["size"]
        vision = self.dna["vision"]
        r = int((speed - min_speed) / (max_speed - min_speed) * 255)
        g = int((size - min_size) / (max_size - min_size) * 255)
        b = int((vision - min_vision) / (max_vision - min_vision) * 255)
        self.color = (r, g, b)
        self.age = 0
        self.is_alive = True

    @staticmethod
    def from_population_list(count):
        """
        Eşit sayıda preferred_food ile blob listesi oluşturur.
        """
        food_types = settings.FOOD_TYPES
        per_type = count // len(food_types)
        remainder = count % len(food_types)
        blobs = []
        prey_count = int(count * 0.25)
        # Önce prey'leri ekle
        for _ in range(prey_count):
            dna = generate_random_dna(initial=True, aggression=random.uniform(0.0, 0.25))
            dna["size"] = random.uniform(settings.SIZE_MIN, (settings.SIZE_MIN + settings.SIZE_MAX) / 2)
            blobs.append(Blob(dna=dna, initial=True))
        # Kalanları normal şekilde ekle
        for i, food_type in enumerate(food_types):
            n = per_type + (1 if i < remainder else 0)
            for _ in range(n):
                if len(blobs) < count:
                    dna = generate_random_dna(preferred_food=food_type, initial=True)
                    blobs.append(Blob(dna=dna, initial=True))
        random.shuffle(blobs)
        return blobs

    @property
    def max_energy(self):
        return settings.BLOB_MAX_ENERGY

    def _pick_new_wander_target(self):
        margin = settings.BLOB_RADIUS
        tx = random.uniform(margin, settings.SCREEN_WIDTH - margin)
        ty = random.uniform(margin, settings.SCREEN_HEIGHT - margin)
        self.wander_target = (tx, ty)

    def update(self, visible_foods: list, visible_blobs: list = None, day_night_ratio: float = 0.0, blobs=None, zone=None, zone_food_count=None):
        """
        Blob'un davranışını günceller. Tür bazlı davranışlar ve zone mantığı uygulanır.
        """
        # --- Metabolizma tipi ve gün/gece etkisi ---
        metabolism = self.dna["metabolism"]
        if metabolism == "day":
            speed_factor = settings.DAY_METABOLISM_SPEED_FACTOR * (1.0 - day_night_ratio) + settings.NIGHT_METABOLISM_SPEED_FACTOR * day_night_ratio
            energy_factor = settings.DAY_METABOLISM_ENERGY_FACTOR * (1.0 - day_night_ratio) + settings.NIGHT_METABOLISM_ENERGY_FACTOR * day_night_ratio
        elif metabolism == "night":
            speed_factor = settings.DAY_BONUS_SPEED_FACTOR * (1.0 - day_night_ratio) + settings.NIGHT_BONUS_SPEED_FACTOR * day_night_ratio
            energy_factor = settings.DAY_BONUS_ENERGY_FACTOR * (1.0 - day_night_ratio) + settings.NIGHT_BONUS_ENERGY_FACTOR * day_night_ratio
        else:
            speed_factor = settings.NEUTRAL_SPEED_FACTOR
            energy_factor = settings.NEUTRAL_ENERGY_FACTOR

        # --- Tür ve zone bilgisi ---
        species = self.species
        aggression = self.dna["aggression"]
        can_attack = False
        # --- Tür bazlı saldırı mantığı ---
        if species == 'herbivore':
            can_attack = False  # Asla saldırmaz
        elif species == 'omnivore':
            if self.energy < 0.3 * self.max_energy and aggression > 0.4:
                can_attack = True
        elif species == 'predator':
            # Sadece günde bir kez saldırabilir
            if not hasattr(self, 'last_attack_frame') or self.last_attack_frame != int(day_night_ratio*1000):
                can_attack = True
        elif species == 'hybrid':
            can_attack = aggression > 0.5
        # --- Central zone avoidance ---
        if zone == 'E' and zone_food_count is not None and zone_food_count > 0:
            # Eğer kendi zone'unda yeterli yiyecek varsa merkeze gitme
            if zone_food_count > 5:
                self.avoid_central = True
            else:
                self.avoid_central = False
        # --- Avcılık ve kaçma kararları ---
        target_blob = None
        flee_blob = None
        self._flee_blob = None
        if visible_blobs is not None:
            if can_attack:
                huntable = [b for b in visible_blobs if b is not self and b.dna["size"] < self.dna["size"] * 0.9 and (species != 'herbivore')]
                if huntable:
                    target_blob = min(huntable, key=lambda b: math.hypot(self.x - b.x, self.y - b.y))
                    self.hunt_target = target_blob
                    if species == 'predator':
                        self.last_attack_frame = int(day_night_ratio*1000)
            elif aggression < 0.4:
                threats = [b for b in visible_blobs if b is not self and b.dna["size"] > self.dna["size"] * 1.1 and b.dna["aggression"] > 0.6]
                if threats:
                    flee_blob = min(threats, key=lambda b: math.hypot(self.x - b.x, self.y - b.y))
                    self._flee_blob = flee_blob
                    self.flee_target = flee_blob
                else:
                    self._flee_blob = None
                    self.flee_target = None
        # Hedef belirleme
        if target_blob:
            # Avcı: Avına yönel
            dx = target_blob.x - self.x
            dy = target_blob.y - self.y
            distance = math.hypot(dx, dy)
            if distance > 0:
                step = self.dna["speed"] * speed_factor
                move_x = (dx / distance) * step
                move_y = (dy / distance) * step
                self.x += move_x
                self.y += move_y
            self.target = target_blob
        elif flee_blob:
            # --- Kaçma davranışını akıllılaştır ---
            if not hasattr(self, '_flee_direction') or self._flee_direction is None or self.flee_target != flee_blob:
                dx = self.x - flee_blob.x
                dy = self.y - flee_blob.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    self._flee_direction = (dx / dist, dy / dist)
                else:
                    self._flee_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
                self._flee_from = flee_blob
            # Kaçış yönünde devam et
            move_x = self._flee_direction[0] * self.dna["speed"] * speed_factor * 1.4
            move_y = self._flee_direction[1] * self.dna["speed"] * speed_factor * 1.4
            self.x += move_x
            self.y += move_y
            self.target = None
        elif visible_foods:
            # Normal: En yakın food'u bul
            closest_food = min(visible_foods, key=lambda food: math.hypot(self.x - food.x, self.y - food.y))
            self.target = closest_food
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.hypot(dx, dy)
            if distance < self.dna["speed"] * speed_factor:
                # Çok yakında titreşim engelle: doğrudan hedefe konumlan
                self.x = self.target.x
                self.y = self.target.y
            elif distance > 0:
                step = self.dna["speed"] * speed_factor
                move_x = (dx / distance) * step
                move_y = (dy / distance) * step
                self.x += move_x
                self.y += move_y
        else:
            # Hedef yoksa: wander_target'a ilerle
            if self.wander_target is None:
                self._pick_new_wander_target()
            tx, ty = self.wander_target
            dx = tx - self.x
            dy = ty - self.y
            distance = math.hypot(dx, dy)
            step = self.dna["speed"] * speed_factor
            if distance < step:
                self.x = tx
                self.y = ty
                self._pick_new_wander_target()
            else:
                move_x = (dx / distance) * step
                move_y = (dy / distance) * step
                self.x += move_x
                self.y += move_y
            # Kenara çarptıysa yeni wander_target seç
            margin = settings.BLOB_RADIUS
            if (self.x <= margin or self.x >= settings.SCREEN_WIDTH - margin or
                self.y <= margin or self.y >= settings.SCREEN_HEIGHT - margin):
                self._pick_new_wander_target()

        # Sınırları aşmasın
        self.x = max(settings.BLOB_RADIUS, min(self.x, settings.SCREEN_WIDTH - settings.BLOB_RADIUS))
        self.y = max(settings.BLOB_RADIUS, min(self.y, settings.SCREEN_HEIGHT - settings.BLOB_RADIUS))
        # --- Enerji kaybı: genetik özelliklere göre ---
        speed = self.dna["speed"]
        size = self.dna["size"]
        vision = self.dna["vision"]
        metabolism_efficiency = energy_factor
        energy_loss = (
            settings.BASE_SPEED_COST * speed +
            settings.BASE_SIZE_COST * size +
            settings.BASE_VISION_COST * vision
        ) * metabolism_efficiency
        # Aşırı kalabalıkta enerji tüketimini artır
        if blobs is not None and len(blobs) > settings.POP_OVERLOAD_LIMIT:
            overload = (len(blobs) - settings.POP_OVERLOAD_LIMIT) * settings.POP_OVERLOAD_MULTIPLIER
            energy_loss *= (1 + overload)
        self.energy -= energy_loss
        # TODO: Enerji kaybı daha gerçekçi hale getirilebilir
        # update sonunda hedefler yoksa None'a çek
        if not target_blob:
            self.hunt_target = None
        if not flee_blob:
            self.flee_target = None
        # Eğer tekrar hedefli moda geçerse wander_target'ı sıfırla
        if visible_foods:
            self.wander_target = None

        # --- Kaçma davranışını akıllılaştır ---
        if flee_blob:
            # Eğer yeni bir tehdit algılandıysa, kaçış yönünü kaydet
            if not hasattr(self, '_flee_direction') or self._flee_direction is None or self.flee_target != flee_blob:
                dx = self.x - flee_blob.x
                dy = self.y - flee_blob.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    self._flee_direction = (dx / dist, dy / dist)
                else:
                    self._flee_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
                self._flee_from = flee_blob
            # Kaçış yönünde devam et
            move_x = self._flee_direction[0] * self.dna["speed"] * speed_factor * 1.4
            move_y = self._flee_direction[1] * self.dna["speed"] * speed_factor * 1.4
            self.x += move_x
            self.y += move_y
            self.target = None
        elif hasattr(self, '_flee_direction') and self._flee_direction is not None:
            # Tehdit görüş alanında değilse, kaçışa devam et
            self.x += self._flee_direction[0] * self.dna["speed"] * speed_factor * 1.4
            self.y += self._flee_direction[1] * self.dna["speed"] * speed_factor * 1.4
            self.target = None
            # Eğer tekrar tehdit görüş alanına girerse, yeni tehdit algıla
            if visible_blobs is not None:
                threats = [b for b in visible_blobs if b is not self and b.dna["size"] > self.dna["size"] * 1.1 and b.dna["aggression"] > 0.6]
                if threats:
                    self._flee_direction = None  # Yeni tehdit algıla
        else:
            self._flee_direction = None

        if self.hunt_cooldown > 0:
            self.hunt_cooldown -= 1

        self.age += 1
        # Enerji çok azsa öl
        if self.energy < settings.MIN_ENERGY_THRESHOLD:
            self.is_alive = False
        # Yaşlılık ölümü
        if self.age > settings.AGE_LIMIT and random.random() < 0.05:
            self.is_alive = False

    def can_eat(self, food):
        """
        Kendi preferred_food türünde ise 1.0, değilse settings.EFFICIENCY_NON_PREF_FOOD oranı döndürür.
        """
        return 1.0 if food.food_type == self.dna["preferred_food"] else settings.EFFICIENCY_NON_PREF_FOOD

    def draw(self, screen):
        """
        Blob'u ekrana çizer. Renk, enerji halkası ve görüş alanı kullanıcı ayarlarına göre değişir.
        """
        base_radius = int(self.dna["size"])
        center = (int(self.x), int(self.y))

        # Fade-out (ölüm animasyonu)
        if hasattr(self, 'fade_alpha') and self.energy <= 0:
            self.fade_alpha = max(0, self.fade_alpha - 10)
            if self.fade_alpha > 0:
                fade_surf = pygame.Surface((base_radius*2+8, base_radius*2+8), pygame.SRCALPHA)
                color = (80, 80, 80, self.fade_alpha)
                pygame.draw.circle(fade_surf, color, (base_radius+4, base_radius+4), base_radius+2)
                screen.blit(fade_surf, (center[0]-base_radius-4, center[1]-base_radius-4))
            return
        # Aggression'a göre aura efekti (daha soft)
        if settings.SHOW_AGGRESSION_AURA:
            aggression = self.dna["aggression"]
            def lerp_color(c1, c2, t):
                return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
            aura_color = lerp_color(settings.AGGRESSION_COLOR_LOW, settings.AGGRESSION_COLOR_HIGH, aggression)
            aura_radius = base_radius + 10
            aura_alpha = int(30 + 80 * aggression)  # Daha soft
            aura_surf = pygame.Surface((aura_radius*2+8, aura_radius*2+8), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, aura_color + (aura_alpha,), (aura_radius+4, aura_radius+4), aura_radius)
            screen.blit(aura_surf, (center[0]-aura_radius-4, center[1]-aura_radius-4))
        # Yeni doğan efektleri: büyüme ve solukluk (daha soft)
        if self.is_newborn and settings.SHOW_NEWBORN_GLOW:
            grow_ratio = min(1.0, self.newborn_age / self.newborn_max_age)
            radius = max(2, int(base_radius * (0.5 + 0.5 * grow_ratio)))
            alpha = int(60 + 80 * (1 - grow_ratio))
            surf = pygame.Surface((radius*2+8, radius*2+8), pygame.SRCALPHA)
            pygame.draw.circle(surf, NEWBORN_COLOR + (alpha,), (radius+4, radius+4), radius)
            screen.blit(surf, (center[0]-radius-4, center[1]-radius-4))
        else:
            radius = base_radius
        # Enerjiye göre parlak aura (glow) efekti (daha soft)
        if settings.SHOW_ENERGY_GLOW and self.energy > 0.9 * self.max_energy:
            glow_radius = radius + 6
            glow_surf = pygame.Surface((glow_radius*2+8, glow_radius*2+8), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf,
                ENERGY_COLOR + (80,),
                (glow_radius+4, glow_radius+4),
                glow_radius,
                0
            )
            screen.blit(glow_surf, (center[0]-glow_radius-4, center[1]-glow_radius-4))

        # Renk seçimi: metabolizma tipine göre veya siyah
        if settings.SHOW_METABOLISM_COLOR:
            color = COLOR_MAP[self.dna["metabolism"]]
        else:
            color = (0, 0, 0)

        # Enerjiye göre alpha (saydamlık) uygula (eski mod)
        if settings.SHOW_ENERGY_ALPHA:
            alpha = int(40 + 215 * max(0, min(self.energy / settings.BLOB_INITIAL_ENERGY, 1)))
            surf = pygame.Surface((radius*2+2, radius*2+2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color + (alpha,), (radius+1, radius+1), radius)
            screen.blit(surf, (center[0]-radius-1, center[1]-radius-1))
        else:
            pygame.draw.circle(screen, color, center, radius)

        # Enerjiye göre dış halka (enerji çemberi)
        if settings.SHOW_ENERGY_CIRCLE:
            pygame.draw.circle(screen, ENERGY_COLOR, center, radius + 2, 2)

        # Görüş alanı çizimi (ince, mavi çizgi)
        if settings.SHOW_VISION:
            vision_radius = int(self.dna["vision"])
            # Vision çemberi daha soft ve degrade efektli
            vision_alpha = max(8, int(18 + 30 * (1 - min(vision_radius / 180, 1))))  # Büyük vision'larda daha da saydam
            vision_surf = pygame.Surface((vision_radius*2+2, vision_radius*2+2), pygame.SRCALPHA)
            # Soft degrade için iç içe birkaç çember
            for i in range(3):
                alpha = int(vision_alpha * (1 - i * 0.33))
                pygame.draw.circle(
                    vision_surf,
                    (50, 100, 255, alpha),
                    (vision_radius+1, vision_radius+1),
                    vision_radius - i*3,
                    0
                )
            screen.blit(vision_surf, (center[0]-vision_radius-1, center[1]-vision_radius-1))

        # preferred_food çerçevesi
        pf_color = settings.FOOD_TYPE_COLORS[self.dna["preferred_food"]]
        pygame.draw.circle(screen, pf_color, center, radius + 4, 2)

        # Avcılık/kaçma çizgileri
        if settings.SHOW_HUNT_LINES:
            # Avcı: hedef blob'a kırmızı çizgi
            if self.hunt_target is not None:
                pygame.draw.line(screen, (255, 60, 60), center, (int(self.hunt_target.x), int(self.hunt_target.y)), 2)
            # Kaçan: tehdit blob'una mavi çizgi
            if self.flee_target is not None:
                pygame.draw.line(screen, (80, 200, 255), center, (int(self.flee_target.x), int(self.flee_target.y)), 2)

        # TODO: Enerjiye göre başka görsel efektler eklenebilir

    def is_dead(self):
        """
        Blob'un ölüp ölmediğini kontrol eder (enerji <= 0 ise ölü).
        """
        return self.energy <= 0 or not self.is_alive
