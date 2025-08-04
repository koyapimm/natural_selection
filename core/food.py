"""
Ecosim Food - Yiyecek Sistemi
"""

import numpy as np
import random
from typing import Optional, Dict, Any
from .utils import logger

class Food:
    """Yiyecek sınıfı - organizmaların enerji kaynağı"""
    
    def __init__(self, position: np.ndarray, energy_value: float = 10.0, 
                 food_type: str = 'basic', decay_rate: float = 0.0):
        """
        Args:
            position: Yiyeceğin pozisyonu
            energy_value: Enerji değeri
            food_type: Yiyecek türü ('basic', 'premium', 'toxic')
            decay_rate: Bozulma hızı (0 = bozulmaz)
        """
        self.position = np.array(position, dtype=np.float32)
        self.energy_value = energy_value
        self.food_type = food_type
        self.decay_rate = decay_rate
        
        # Fiziksel özellikler
        self.size = random.uniform(2.0, 6.0)  # Boyut varyasyonu eklendi
        self.color = self._get_color_by_type()
        self.age = 0.0
        
        # Özel özellikler
        self.is_moving = False
        self.movement_speed = 0.0
        self.movement_direction = np.array([0.0, 0.0])
        
        # İstatistikler
        self.stats = {
            'created_at': 0,  # frame numarası
            'eaten_at': None,
            'lifetime': 0.0
        }
        
        logger.debug(f"🍎 Food oluşturuldu: {position}, type: {food_type}")
    
    def _get_color_by_type(self) -> tuple:
        """Yiyecek türüne göre renk belirle"""
        if self.food_type == 'basic':
            return (0, 255, 0)  # Yeşil
        elif self.food_type == 'premium':
            return (255, 215, 0)  # Altın
        elif self.food_type == 'toxic':
            return (255, 0, 0)  # Kırmızı
        elif self.food_type == 'nutritious':
            return (0, 255, 255)  # Cyan
        else:
            return (0, 255, 0)  # Varsayılan yeşil
    
    def update(self, delta_time: float, frame: int):
        """Yiyeceği güncelle"""
        self.age += delta_time
        self.stats['lifetime'] = self.age
        
        # Bozulma kontrolü
        if self.decay_rate > 0:
            self.energy_value -= self.decay_rate * delta_time
            if self.energy_value <= 0:
                return False  # Yiyecek bozuldu
        
        # Hareket güncelleme
        if self.is_moving:
            self._update_movement(delta_time)
        
        return True
    
    def _update_movement(self, delta_time: float):
        """Hareketli yiyecekler için hareket güncelleme"""
        if self.movement_speed > 0:
            # Rastgele yön değişimi
            if random.random() < 0.01:  # %1 şans
                angle = random.uniform(0, 2 * np.pi)
                self.movement_direction = np.array([
                    np.cos(angle),
                    np.sin(angle)
                ])
            
            # Pozisyonu güncelle
            self.position += self.movement_direction * self.movement_speed * delta_time
    
    def get_effect_on_organism(self, organism) -> Dict[str, float]:
        """Yiyeceğin organizma üzerindeki etkisini hesapla"""
        effects = {
            'energy_gain': self.energy_value,
            'speed_modifier': 1.0,
            'health_modifier': 1.0
        }
        
        if self.food_type == 'premium':
            effects['energy_gain'] *= 1.5
            effects['speed_modifier'] = 1.2
        elif self.food_type == 'toxic':
            effects['energy_gain'] *= 0.5
            effects['health_modifier'] = 0.8
        elif self.food_type == 'nutritious':
            effects['energy_gain'] *= 1.3
            effects['health_modifier'] = 1.1
        
        return effects
    
    def is_edible(self) -> bool:
        """Yiyeceğin yenilebilir olup olmadığını kontrol et"""
        return self.energy_value > 0 and self.food_type != 'toxic'
    
    def get_info(self) -> Dict[str, Any]:
        """Yiyecek hakkında bilgi döndür"""
        return {
            'position': self.position.tolist(),
            'energy_value': self.energy_value,
            'food_type': self.food_type,
            'age': self.age,
            'is_edible': self.is_edible(),
            'stats': self.stats
        }

class FoodSpawner:
    """Yiyecek üretici sınıfı"""
    
    def __init__(self, world_size: tuple, spawn_config: Dict[str, Any]):
        """
        Args:
            world_size: Dünya boyutu
            spawn_config: Üretim yapılandırması
        """
        self.world_size = world_size
        self.spawn_config = spawn_config
        
        # Üretim istatistikleri
        self.stats = {
            'total_spawned': 0,
            'spawned_by_type': {}
        }
        
        logger.info(f"🍎 FoodSpawner oluşturuldu: {world_size}")
    
    def spawn_food(self, frame: int) -> Optional[Food]:
        """Yeni yiyecek üret"""
        try:
            # Üretim olasılığını kontrol et
            spawn_rate = self.spawn_config.get('spawn_rate', 0.05)
            if random.random() > spawn_rate:
                return None
            
            # Pozisyon belirle
            position = self._get_spawn_position()
            
            # Yiyecek türü belirle
            food_type = self._get_random_food_type()
            
            # Yiyecek özelliklerini belirle
            energy_value = self._get_energy_value(food_type)
            decay_rate = self._get_decay_rate(food_type)
            
            # Yiyecek oluştur
            food = Food(
                position=position,
                energy_value=energy_value,
                food_type=food_type,
                decay_rate=decay_rate
            )
            
            # Hareketli yiyecek kontrolü
            if self.spawn_config.get('moving_food_probability', 0.0) > random.random():
                food.is_moving = True
                food.movement_speed = random.uniform(10, 30)
                angle = random.uniform(0, 2 * np.pi)
                food.movement_direction = np.array([np.cos(angle), np.sin(angle)])
            
            # İstatistikleri güncelle
            food.stats['created_at'] = frame
            self.stats['total_spawned'] += 1
            self.stats['spawned_by_type'][food_type] = \
                self.stats['spawned_by_type'].get(food_type, 0) + 1
            
            return food
            
        except Exception as e:
            logger.error(f"Yiyecek üretilirken hata: {e}")
            return None
    
    def _get_spawn_position(self) -> np.ndarray:
        """Üretim pozisyonu belirle"""
        # Basit rastgele pozisyon
        x = random.uniform(0, self.world_size[0])
        y = random.uniform(0, self.world_size[1])
        
        # Özel üretim bölgeleri kontrolü
        spawn_zones = self.spawn_config.get('spawn_zones', [])
        if spawn_zones:
            zone = random.choice(spawn_zones)
            x = random.uniform(zone['x_min'], zone['x_max'])
            y = random.uniform(zone['y_min'], zone['y_max'])
        
        return np.array([x, y])
    
    def _get_random_food_type(self) -> str:
        """Rastgele yiyecek türü seç"""
        food_types = self.spawn_config.get('food_types', {
            'basic': 0.7,
            'premium': 0.2,
            'nutritious': 0.1
        })
        
        # Ağırlıklı rastgele seçim
        total_weight = sum(food_types.values())
        rand_val = random.uniform(0, total_weight)
        
        current_weight = 0
        for food_type, weight in food_types.items():
            current_weight += weight
            if rand_val <= current_weight:
                return food_type
        
        return 'basic'  # Varsayılan
    
    def _get_energy_value(self, food_type: str) -> float:
        """Yiyecek türüne göre enerji değeri belirle"""
        base_energy = self.spawn_config.get('base_energy', 10.0)
        
        energy_multipliers = {
            'basic': 1.0,
            'premium': 1.5,
            'nutritious': 1.3,
            'toxic': 0.5
        }
        
        multiplier = energy_multipliers.get(food_type, 1.0)
        return base_energy * multiplier
    
    def _get_decay_rate(self, food_type: str) -> float:
        """Yiyecek türüne göre bozulma hızı belirle"""
        base_decay = self.spawn_config.get('base_decay_rate', 0.0)
        
        decay_multipliers = {
            'basic': 1.0,
            'premium': 0.5,  # Premium yiyecekler daha yavaş bozulur
            'nutritious': 0.8,
            'toxic': 0.0  # Zehirli yiyecekler bozulmaz
        }
        
        multiplier = decay_multipliers.get(food_type, 1.0)
        return base_decay * multiplier
    
    def get_statistics(self) -> Dict[str, Any]:
        """Üretim istatistiklerini döndür"""
        return {
            **self.stats,
            'spawn_rate': self.spawn_config.get('spawn_rate', 0.05),
            'active_zones': len(self.spawn_config.get('spawn_zones', []))
        } 