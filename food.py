"""
food.py
Simülasyondaki sabit enerji kaynağı (Food) sınıfı.
Yiyecekler, blob'lar tarafından tüketilmek üzere sabit bir konumda bulunur.
"""

import random
import pygame
from settings import COLOR_FOOD, FOOD_RADIUS, ENERGY_PER_FOOD, SCREEN_WIDTH, SCREEN_HEIGHT, FOOD_LIFESPAN, FOOD_TYPES, FOOD_TYPE_COLORS, SHOW_ROTTEN_FOOD

class Food:
    def __init__(self, birth_frame=0, food_type=None):
        """
        Rastgele bir konumda, belirli bir türde sabit enerjiye sahip bir yiyecek oluşturur.
        food_type: "green", "red" veya "blue" (varsayılan: rastgele)
        """
        self.x = random.uniform(FOOD_RADIUS, SCREEN_WIDTH - FOOD_RADIUS)
        self.y = random.uniform(FOOD_RADIUS, SCREEN_HEIGHT - FOOD_RADIUS)
        self.is_eaten = False  # Yiyeceğin tüketilip tüketilmediği (ileride kullanılacak)
        self.birth_frame = birth_frame
        self.is_rotten = False  # Çürümüş mü?
        self.food_type = food_type if food_type is not None else random.choice(FOOD_TYPES)
        # Enerji değeri food_type'a göre belirlenir
        if self.food_type == 'green':
            self.energy = ENERGY_PER_FOOD
        elif self.food_type == 'red':
            self.energy = ENERGY_PER_FOOD * 4.0
        elif self.food_type == 'blue':
            self.energy = ENERGY_PER_FOOD * 2.5
        else:
            self.energy = ENERGY_PER_FOOD

    def update(self, current_frame=None):
        """
        Yiyecekler şimdilik güncellenmez, ancak çürüme kontrolü yapılır.
        current_frame: Simülasyonun global frame sayacı
        """
        if current_frame is not None:
            if (current_frame - self.birth_frame) >= FOOD_LIFESPAN:
                self.is_rotten = True

    def draw(self, screen):
        """
        Yiyeceği ekrana küçük bir daire olarak çizer.
        """
        color = FOOD_TYPE_COLORS[self.food_type]
        if self.is_rotten and SHOW_ROTTEN_FOOD:
            # Çürümüş yiyecekler %50 opacity ile veya daha koyu tonda çizilir
            rotten_color = tuple(int(c * 0.5) for c in color)
            surf = pygame.Surface((FOOD_RADIUS*2+2, FOOD_RADIUS*2+2), pygame.SRCALPHA)
            pygame.draw.circle(surf, rotten_color + (128,), (FOOD_RADIUS+1, FOOD_RADIUS+1), FOOD_RADIUS)
            screen.blit(surf, (int(self.x)-FOOD_RADIUS-1, int(self.y)-FOOD_RADIUS-1))
        else:
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), FOOD_RADIUS)

    def can_be_eaten_by(self, blob):
        # Blue sadece neutral metabolizma tarafından sindirilebilir
        if self.food_type == 'blue' and blob.dna['metabolism'] != 'neutral':
            return False
        return True 