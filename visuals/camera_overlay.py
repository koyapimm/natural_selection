"""
Kamera Overlay Sistemi
"""

import pygame
import numpy as np
from typing import Tuple, List, Dict, Any
from core.utils import logger

class CameraOverlay:
    """Kamera üzerinde görsel bilgiler gösteren sınıf"""
    
    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_size = screen_size
        self.width, self.height = screen_size
        
        # Grid ayarları
        self.grid_enabled = True
        self.grid_size = 100
        self.grid_color = (50, 50, 50, 100)
        
        # Koordinat sistemi
        self.coords_enabled = True
        self.coord_font = pygame.font.Font(None, 16)
        
        # Seçim kutusu
        self.selection_box = None
        self.selection_start = None
        self.selection_end = None
        
        # Hedef göstergesi
        self.target_indicator = None
        self.target_organism = None
        
        logger.info("📷 CameraOverlay oluşturuldu")
    
    def draw_grid(self, screen: pygame.Surface, camera):
        """Grid çiz"""
        if not self.grid_enabled:
            return
        
        # Grid boyutunu zoom'a göre ayarla
        grid_size = max(20, int(self.grid_size / camera.zoom_level))
        
        # Dünya koordinatlarını al
        world_top_left = camera.screen_to_world(np.array([0, 0]))
        world_bottom_right = camera.screen_to_world(self.screen_size)
        
        # Grid başlangıç ve bitiş noktaları
        start_x = int(world_top_left[0] // grid_size) * grid_size
        start_y = int(world_top_left[1] // grid_size) * grid_size
        end_x = int(world_bottom_right[0] // grid_size) * grid_size + grid_size
        end_y = int(world_bottom_right[1] // grid_size) * grid_size + grid_size
        
        # Dikey çizgiler
        for x in range(int(start_x), int(end_x), int(grid_size)):
            screen_pos = camera.world_to_screen(np.array([x, 0]))
            if 0 <= screen_pos[0] <= self.width:
                pygame.draw.line(screen, self.grid_color, 
                               (screen_pos[0], 0), (screen_pos[0], self.height), 1)
        
        # Yatay çizgiler
        for y in range(int(start_y), int(end_y), int(grid_size)):
            screen_pos = camera.world_to_screen(np.array([0, y]))
            if 0 <= screen_pos[1] <= self.height:
                pygame.draw.line(screen, self.grid_color, 
                               (0, screen_pos[1]), (self.width, screen_pos[1]), 1)
    
    def draw_coordinates(self, screen: pygame.Surface, camera):
        """Koordinat bilgilerini çiz"""
        if not self.coords_enabled:
            return
        
        # Ekran köşelerindeki koordinatları göster
        corners = [
            (10, 10),  # Sol üst
            (self.width - 100, 10),  # Sağ üst
            (10, self.height - 30),  # Sol alt
            (self.width - 100, self.height - 30)  # Sağ alt
        ]
        
        world_positions = [
            camera.screen_to_world(np.array([0, 0])),  # Sol üst
            camera.screen_to_world(np.array([self.width, 0])),  # Sağ üst
            camera.screen_to_world(np.array([0, self.height])),  # Sol alt
            camera.screen_to_world(np.array([self.width, self.height]))  # Sağ alt
        ]
        
        for i, (screen_pos, world_pos) in enumerate(zip(corners, world_positions)):
            coord_text = f"({world_pos[0]:.0f}, {world_pos[1]:.0f})"
            text_surface = self.coord_font.render(coord_text, True, (200, 200, 200))
            screen.blit(text_surface, screen_pos)
    
    def draw_selection_box(self, screen: pygame.Surface, camera):
        """Seçim kutusunu çiz"""
        if self.selection_start is None or self.selection_end is None:
            return
        
        # Seçim kutusu koordinatları
        x1, y1 = self.selection_start
        x2, y2 = self.selection_end
        
        # Kutu çiz
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pygame.draw.rect(screen, (0, 255, 255), rect, 2)
        
        # Seçim alanındaki organizmaları vurgula
        world_start = camera.screen_to_world(np.array([min(x1, x2), min(y1, y2)]))
        world_end = camera.screen_to_world(np.array([max(x1, x2), max(y1, y2)]))
        
        # Bu alanı daha sonra organizma seçimi için kullanabiliriz
        self.selection_area = (world_start, world_end)
    
    def draw_target_indicator(self, screen: pygame.Surface, camera):
        """Hedef göstergesini çiz"""
        if self.target_organism is None:
            return
        
        # Hedef organizmanın ekran pozisyonu
        screen_pos = camera.world_to_screen(self.target_organism.position)
        
        # Hedef çemberi
        radius = 20
        pygame.draw.circle(screen, (255, 255, 0), (int(screen_pos[0]), int(screen_pos[1])), radius, 2)
        
        # Hedef işareti
        pygame.draw.circle(screen, (255, 255, 0), (int(screen_pos[0]), int(screen_pos[1])), 3)
        
        # Hedef bilgisi
        font = pygame.font.Font(None, 18)
        target_text = f"Hedef: #{self.target_organism.organism_id}"
        text_surface = font.render(target_text, True, (255, 255, 0))
        screen.blit(text_surface, (int(screen_pos[0]) + radius + 5, int(screen_pos[1]) - 10))
    
    def draw_zoom_indicator(self, screen: pygame.Surface, camera):
        """Zoom göstergesini çiz"""
        zoom_text = f"Zoom: {camera.zoom_level:.2f}x"
        font = pygame.font.Font(None, 20)
        text_surface = font.render(zoom_text, True, (255, 255, 255))
        
        # Sağ üst köşede göster
        text_rect = text_surface.get_rect()
        text_rect.topright = (self.width - 10, 10)
        screen.blit(text_surface, text_rect)
    
    def draw_camera_info(self, screen: pygame.Surface, camera):
        """Kamera bilgilerini çiz"""
        # Kamera pozisyonu
        pos_text = f"Kamera: ({camera.position[0]:.0f}, {camera.position[1]:.0f})"
        font = pygame.font.Font(None, 16)
        text_surface = font.render(pos_text, True, (200, 200, 200))
        
        # Sol alt köşede göster
        text_rect = text_surface.get_rect()
        text_rect.bottomleft = (10, self.height - 40)
        screen.blit(text_surface, text_rect)
        
        # Görünür alan bilgisi
        visible_area = camera.get_visible_area()
        area_text = f"Görünür Alan: {visible_area[0][0]:.0f},{visible_area[0][1]:.0f} - {visible_area[1][0]:.0f},{visible_area[1][1]:.0f}"
        area_surface = font.render(area_text, True, (200, 200, 200))
        
        area_rect = area_surface.get_rect()
        area_rect.bottomleft = (10, self.height - 20)
        screen.blit(area_surface, area_rect)
    
    def start_selection(self, screen_pos: Tuple[int, int]):
        """Seçim başlat"""
        self.selection_start = screen_pos
        self.selection_end = screen_pos
    
    def update_selection(self, screen_pos: Tuple[int, int]):
        """Seçimi güncelle"""
        if self.selection_start is not None:
            self.selection_end = screen_pos
    
    def end_selection(self):
        """Seçimi bitir"""
        self.selection_start = None
        self.selection_end = None
        self.selection_area = None
    
    def set_target_organism(self, organism):
        """Hedef organizmayı ayarla"""
        self.target_organism = organism
    
    def clear_target(self):
        """Hedefi temizle"""
        self.target_organism = None
    
    def toggle_grid(self):
        """Grid'i aç/kapat"""
        self.grid_enabled = not self.grid_enabled
    
    def toggle_coordinates(self):
        """Koordinatları aç/kapat"""
        self.coords_enabled = not self.coords_enabled
    
    def draw_all_overlays(self, screen: pygame.Surface, camera):
        """Tüm overlay'leri çiz"""
        # Grid
        self.draw_grid(screen, camera)
        
        # Koordinatlar
        self.draw_coordinates(screen, camera)
        
        # Seçim kutusu
        self.draw_selection_box(screen, camera)
        
        # Hedef göstergesi
        self.draw_target_indicator(screen, camera)
        
        # Zoom göstergesi
        self.draw_zoom_indicator(screen, camera)
        
        # Kamera bilgileri
        self.draw_camera_info(screen, camera) 