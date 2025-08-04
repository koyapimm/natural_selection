"""
Yiyecek Görselleştirme Sistemi
"""

import pygame
from typing import Tuple, Dict, Any
from core.utils import logger

class FoodRenderer:
    """Yiyecekleri görselleştiren sınıf"""
    
    def __init__(self):
        # Yiyecek türü renkleri
        self.food_type_colors = {
            'basic': (0, 255, 0),      # Yeşil
            'premium': (255, 215, 0),  # Altın
            'nutritious': (0, 255, 255), # Cyan
            'toxic': (255, 0, 255),    # Magenta
        }
        
        # Yiyecek türü şekilleri
        self.food_type_shapes = {
            'basic': 'circle',
            'premium': 'diamond',
            'nutritious': 'star',
            'toxic': 'cross',
        }
        
        logger.info("🍎 FoodRenderer oluşturuldu")
    
    def draw_food(self, screen: pygame.Surface, food, camera, show_details: bool = False):
        """Yiyeceği çiz"""
        # Dünya koordinatlarını ekran koordinatlarına çevir
        screen_pos = camera.world_to_screen(food.position)
        screen_x, screen_y = int(screen_pos[0]), int(screen_pos[1])
        
        # Boyut hesaplama (görsel kalite iyileştirildi)
        base_size = max(5, int(food.size * camera.zoom_level * 2.0))
        
        # Yiyecek türü rengi
        food_color = self.food_type_colors.get(food.food_type, (0, 255, 0))
        
        # Yiyecek şekli
        shape = self.food_type_shapes.get(food.food_type, 'circle')
        
        # Ana yiyecek çizimi
        self._draw_food_shape(screen, screen_x, screen_y, base_size, food_color, shape)
        
        # Enerji değeri (zoom yüksekse)
        if show_details and camera.zoom_level > 2.0:
            self._draw_food_details(screen, screen_x, screen_y, base_size, food)
        
        # Hareket efekti (hareketli yiyecekler için)
        if hasattr(food, 'is_moving') and food.is_moving:
            self._draw_movement_trail(screen, screen_x, screen_y, base_size, food_color)
    
    def _draw_food_shape(self, screen: pygame.Surface, x: int, y: int, size: int, 
                        color: Tuple[int, int, int], shape: str):
        """Yiyecek şeklini çiz (profesyonel görünüm)"""
        # Gölge efekti (koyu gri)
        shadow_size = size + 1
        shadow_color = (20, 20, 20)
        pygame.draw.circle(screen, shadow_color, (x + 1, y + 1), shadow_size)
        
        if shape == 'circle':
            # Ana şekil
            pygame.draw.circle(screen, color, (x, y), size)
            # İç parlaklık
            highlight_size = max(2, size // 3)
            highlight_color = tuple(min(255, c + 60) for c in color)
            pygame.draw.circle(screen, highlight_color, (x - highlight_size//2, y - highlight_size//2), highlight_size)
            
        elif shape == 'diamond':
            points = [
                (x, y - size),
                (x + size, y),
                (x, y + size),
                (x - size, y)
            ]
            pygame.draw.polygon(screen, color, points)
            # İç parlaklık (küçük daire)
            highlight_size = max(2, size // 4)
            pygame.draw.circle(screen, (255, 255, 255), (x - highlight_size//2, y - highlight_size//2), highlight_size)
            
        elif shape == 'star':
            # Basit yıldız (5 köşeli)
            import math
            points = []
            for i in range(10):
                angle = i * math.pi / 5
                radius = size if i % 2 == 0 else size // 2
                point_x = x + int(radius * math.cos(angle))
                point_y = y + int(radius * math.sin(angle))
                points.append((point_x, point_y))
            pygame.draw.polygon(screen, color, points)
            # Merkez parlaklık
            pygame.draw.circle(screen, (255, 255, 255), (x, y), max(2, size // 4))
            
        elif shape == 'cross':
            # Artı işareti (daha kalın)
            line_width = max(3, size // 3)
            pygame.draw.line(screen, color, (x - size, y), (x + size, y), line_width)
            pygame.draw.line(screen, color, (x, y - size), (x, y + size), line_width)
            # Merkez parlaklık
            pygame.draw.circle(screen, (255, 255, 255), (x, y), max(2, size // 4))
        
        # Dış parlaklık halkası
        glow_size = size + 2
        glow_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.circle(screen, glow_color, (x, y), glow_size, 2)
    
    def _draw_food_details(self, screen: pygame.Surface, x: int, y: int, size: int, food):
        """Yiyecek detaylarını çiz"""
        font = pygame.font.Font(None, max(12, size * 2))
        
        # Enerji değeri
        energy_text = font.render(f"{int(food.energy_value)}", True, (255, 255, 255))
        screen.blit(energy_text, (x + size + 3, y - size // 2))
        
        # Yiyecek türü
        type_text = font.render(food.food_type[:3], True, (200, 200, 200))
        screen.blit(type_text, (x + size + 3, y + size // 2))
    
    def _draw_movement_trail(self, screen: pygame.Surface, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """Hareket izini çiz"""
        # Hareket yönünde küçük parçacıklar
        trail_length = 3
        for i in range(trail_length):
            offset = (i + 1) * 2
            alpha = 255 - (i * 50)  # Giderek şeffaf
            trail_color = (*color, alpha)
            
            # Basit parçacık efekti
            particle_size = max(1, size // (i + 2))
            pygame.draw.circle(screen, trail_color, (x - offset, y - offset), particle_size)
    
    def get_food_info(self, food) -> Dict[str, Any]:
        """Yiyecek hakkında görsel bilgi döndür"""
        return {
            'position': food.position.tolist(),
            'energy_value': food.energy_value,
            'food_type': food.food_type,
            'color': food.color,
            'size': food.size,
            'is_edible': food.is_edible(),
            'age': food.age
        } 