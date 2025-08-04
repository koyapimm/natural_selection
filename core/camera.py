"""
Ecosim Camera - Kamera ve Görüntüleme Sistemi
"""

import numpy as np
import pygame
from typing import Tuple, Optional, List, Dict, Any
from .utils import logger

class Camera:
    """Kamera sistemi - kullanıcının dünya üzerinde gezinmesini sağlar"""
    
    def __init__(self, screen_size: Tuple[int, int], world_size: Tuple[int, int],
                 zoom_level: float = 1.0):
        """
        Args:
            screen_size: Ekran boyutu (width, height)
            world_size: Dünya boyutu (width, height)
            zoom_level: Başlangıç zoom seviyesi
        """
        self.screen_size = np.array(screen_size, dtype=np.float32)
        self.world_size = np.array(world_size, dtype=np.float32)
        
        # Kamera pozisyonu (dünya koordinatlarında)
        self.position = np.array([0.0, 0.0], dtype=np.float32)
        
        # Zoom ve görüntüleme ayarları
        self.zoom_level = zoom_level
        self.min_zoom = 0.1
        self.max_zoom = 10.0  # Daha yüksek zoom seviyesi
        
        # Kamera hareket ayarları
        self.movement_speed = 400.0  # piksel/saniye
        self.zoom_speed = 0.15  # Daha hızlı zoom
        self.edge_pan_speed = 300.0  # Kenar kaydırma hızı
        self.edge_pan_threshold = 50  # Kenar kaydırma eşiği
        
        # Mouse drag ayarları
        self.drag_enabled = True
        self.is_dragging = False
        self.drag_start_pos = None
        self.drag_start_camera_pos = None
        self.drag_sensitivity = 1.0
        
        # Hedef takibi
        self.target_organism = None
        self.follow_mode = False
        self.smooth_following = True
        self.follow_speed = 0.1
        
        # Görüntüleme optimizasyonu
        self.culling_enabled = True
        self.culling_margin = 100  # Ekran dışındaki margin
        
        # İstatistikler
        self.stats = {
            'total_movement': 0.0,
            'zoom_changes': 0,
            'target_changes': 0,
            'drag_operations': 0
        }
        
        logger.info(f"📷 Camera oluşturuldu: {screen_size}, zoom: {zoom_level}")
    
    def world_to_screen(self, world_pos: np.ndarray) -> np.ndarray:
        """Dünya koordinatlarını ekran koordinatlarına dönüştür"""
        # Kamera pozisyonunu çıkar
        relative_pos = world_pos - self.position
        
        # Zoom uygula
        zoomed_pos = relative_pos * self.zoom_level
        
        # Ekran merkezine kaydır
        screen_pos = zoomed_pos + self.screen_size / 2
        
        return screen_pos
    
    def screen_to_world(self, screen_pos: np.ndarray) -> np.ndarray:
        """Ekran koordinatlarını dünya koordinatlarına dönüştür"""
        # Ekran merkezinden çıkar
        relative_pos = screen_pos - self.screen_size / 2
        
        # Zoom'u geri al
        world_pos = relative_pos / self.zoom_level
        
        # Kamera pozisyonunu ekle
        return world_pos + self.position
    
    def is_visible(self, world_pos: np.ndarray) -> bool:
        """Bir dünya pozisyonunun ekranda görünür olup olmadığını kontrol et"""
        if not self.culling_enabled:
            return True
        
        screen_pos = self.world_to_screen(world_pos)
        
        # Margin ile birlikte kontrol
        margin = self.culling_margin
        return (-margin <= screen_pos[0] <= self.screen_size[0] + margin and
                -margin <= screen_pos[1] <= self.screen_size[1] + margin)
    
    def get_visible_area(self) -> Tuple[np.ndarray, np.ndarray]:
        """Görünür alanın dünya koordinatlarını döndür"""
        # Ekran köşelerini dünya koordinatlarına çevir
        top_left = self.screen_to_world(np.array([0, 0]))
        bottom_right = self.screen_to_world(self.screen_size)
        
        return top_left, bottom_right
    
    def move(self, direction: np.ndarray, delta_time: float):
        """Kamerayı hareket ettir"""
        # Hareket vektörünü hesapla
        movement = direction * self.movement_speed * delta_time / self.zoom_level
        
        # Pozisyonu güncelle
        new_position = self.position + movement
        
        # Dünya sınırları kontrolü
        self.position = self._clamp_to_world_bounds(new_position)
        
        # İstatistikleri güncelle
        self.stats['total_movement'] += np.linalg.norm(movement)
    
    def _clamp_to_world_bounds(self, position: np.ndarray) -> np.ndarray:
        """Pozisyonu dünya sınırları içinde tut"""
        # Kamera yarı boyutunu hesapla
        camera_half_size = self.screen_size / (2 * self.zoom_level)
        
        # Minimum ve maksimum pozisyonları hesapla
        min_pos = camera_half_size
        max_pos = self.world_size - camera_half_size
        
        # Sınırları uygula
        clamped_pos = np.clip(position, min_pos, max_pos)
        
        return clamped_pos
    
    def zoom(self, zoom_delta: float, zoom_center: Optional[np.ndarray] = None):
        """Kamerayı zoom yap"""
        old_zoom = self.zoom_level
        
        # Zoom seviyesini güncelle
        self.zoom_level = np.clip(
            self.zoom_level + zoom_delta * self.zoom_speed,
            self.min_zoom,
            self.max_zoom
        )
        
        # Zoom merkezi belirtilmişse, pozisyonu ayarla
        if zoom_center is not None and zoom_delta != 0:
            # Zoom merkezini dünya koordinatlarına çevir
            world_center = self.screen_to_world(zoom_center)
            
            # Yeni zoom seviyesiyle pozisyonu hesapla
            zoom_ratio = self.zoom_level / old_zoom
            new_position = world_center - (world_center - self.position) * zoom_ratio
            
            # Sınırları kontrol et
            self.position = self._clamp_to_world_bounds(new_position)
        
        # İstatistikleri güncelle
        if old_zoom != self.zoom_level:
            self.stats['zoom_changes'] += 1
    
    def handle_mouse_drag(self, mouse_pos: Tuple[int, int], mouse_buttons: Tuple[bool, bool, bool], delta_time: float):
        """Mouse drag ile kamera hareketi"""
        if not self.drag_enabled:
            return
        
        mouse_pos_array = np.array(mouse_pos)
        
        # Sol tık basılı mı?
        left_button_pressed = mouse_buttons[0]
        
        if left_button_pressed and not self.is_dragging:
            # Drag başlat
            self.is_dragging = True
            self.drag_start_pos = mouse_pos_array
            self.drag_start_camera_pos = self.position.copy()
            
        elif left_button_pressed and self.is_dragging:
            # Drag devam ediyor
            if self.drag_start_pos is not None:
                # Mouse hareketini hesapla
                mouse_delta = mouse_pos_array - self.drag_start_pos
                
                # Dünya koordinatlarına çevir
                world_delta = mouse_delta / self.zoom_level * self.drag_sensitivity
                
                # Kamerayı ters yönde hareket ettir
                new_position = self.drag_start_camera_pos - world_delta
                self.position = self._clamp_to_world_bounds(new_position)
                
                self.stats['drag_operations'] += 1
                
        elif not left_button_pressed and self.is_dragging:
            # Drag bitir
            self.is_dragging = False
            self.drag_start_pos = None
            self.drag_start_camera_pos = None
    
    def handle_edge_pan(self, mouse_pos: Tuple[int, int], delta_time: float):
        """Ekran kenarlarında otomatik kaydırma"""
        mouse_x, mouse_y = mouse_pos
        screen_width, screen_height = self.screen_size
        
        # Hareket vektörü
        movement = np.array([0.0, 0.0])
        
        # Sol kenar
        if mouse_x < self.edge_pan_threshold:
            movement[0] = -1.0
        # Sağ kenar
        elif mouse_x > screen_width - self.edge_pan_threshold:
            movement[0] = 1.0
        
        # Üst kenar
        if mouse_y < self.edge_pan_threshold:
            movement[1] = -1.0
        # Alt kenar
        elif mouse_y > screen_height - self.edge_pan_threshold:
            movement[1] = 1.0
        
        # Hareket varsa uygula
        if np.linalg.norm(movement) > 0:
            # Normalize et
            movement = movement / np.linalg.norm(movement)
            
            # Edge pan hızını uygula
            edge_movement = movement * self.edge_pan_speed * delta_time / self.zoom_level
            new_position = self.position + edge_movement
            self.position = self._clamp_to_world_bounds(new_position)
    
    def follow_organism(self, organism, delta_time: float):
        """Belirli bir organizmayı takip et"""
        if organism is None:
            return
        
        if self.smooth_following:
            # Yumuşak takip
            target_pos = organism.position
            current_pos = self.position
            
            # Hedef pozisyona doğru hareket
            direction = target_pos - current_pos
            distance = np.linalg.norm(direction)
            
            if distance > 0:
                # Yumuşak hareket
                movement = direction * self.follow_speed
                new_position = current_pos + movement
                self.position = self._clamp_to_world_bounds(new_position)
        else:
            # Anında takip
            self.position = organism.position.copy()
            self.position = self._clamp_to_world_bounds(self.position)
    
    def set_target(self, organism):
        """Takip edilecek organizmayı ayarla"""
        self.target_organism = organism
        self.follow_mode = organism is not None
        self.stats['target_changes'] += 1
        
        if organism:
            logger.info(f"📷 Camera hedefi ayarlandı: Organism #{organism.organism_id}")
        else:
            logger.info("📷 Camera hedefi kaldırıldı")
    
    def center_on_position(self, world_pos: np.ndarray):
        """Kamerayı belirli bir pozisyona odakla"""
        self.position = world_pos.copy()
        self.position = self._clamp_to_world_bounds(self.position)
        
        logger.info(f"📷 Camera pozisyona odaklandı: {world_pos}")
    
    def reset_view(self):
        """Kamerayı varsayılan görünüme sıfırla"""
        self.position = np.array([0.0, 0.0])
        self.zoom_level = 1.0
        self.target_organism = None
        self.follow_mode = False
        self.is_dragging = False
        
        logger.info("📷 Camera görünümü sıfırlandı")
    
    def handle_input(self, keys_pressed, mouse_pos: Tuple[int, int],
                    mouse_wheel: int, delta_time: float):
        """Kullanıcı girdilerini işle (genişletilmiş)"""
        # Mouse butonlarını al
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Mouse drag işle
        self.handle_mouse_drag(mouse_pos, mouse_buttons, delta_time)
        
        # Edge pan işle (drag sırasında değilse)
        if not self.is_dragging:
            self.handle_edge_pan(mouse_pos, delta_time)
        
        # Klavye hareketi (drag sırasında devre dışı)
        if not self.is_dragging:
            movement = np.array([0.0, 0.0])
            
            if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
                movement[1] -= 1
            if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
                movement[1] += 1
            if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
                movement[0] -= 1
            if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
                movement[0] += 1
            
            # Hareket vektörünü normalize et
            if np.linalg.norm(movement) > 0:
                movement = movement / np.linalg.norm(movement)
                self.move(movement, delta_time)
        
        # Mouse wheel zoom
        if mouse_wheel != 0:
            mouse_pos_array = np.array(mouse_pos)
            self.zoom(mouse_wheel, mouse_pos_array)
        
        # Hedef takibi
        if self.follow_mode and self.target_organism:
            self.follow_organism(self.target_organism, delta_time)
    
    def get_visible_organisms(self, organisms: List) -> List[int]:
        """Görünür organizmaların indekslerini döndür"""
        visible_indices = []
        
        for i, organism in enumerate(organisms):
            if organism is not None and self.is_visible(organism.position):
                visible_indices.append(i)
        
        return visible_indices
    
    def get_visible_foods(self, foods: List) -> List[int]:
        """Görünür yiyeceklerin indekslerini döndür"""
        visible_indices = []
        
        for i, food in enumerate(foods):
            if food is not None and self.is_visible(food.position):
                visible_indices.append(i)
        
        return visible_indices
    
    def get_info(self) -> Dict[str, Any]:
        """Kamera hakkında bilgi döndür"""
        return {
            'position': self.position.tolist(),
            'zoom_level': self.zoom_level,
            'screen_size': self.screen_size.tolist(),
            'follow_mode': self.follow_mode,
            'is_dragging': self.is_dragging,
            'target_organism_id': self.target_organism.organism_id if self.target_organism else None,
            'stats': self.stats
        } 