"""
Organizma Görselleştirme Sistemi
"""

import pygame
import numpy as np
from typing import Tuple, Dict, Any
from core.utils import logger

class OrganismRenderer:
    """Organizmaları görselleştiren sınıf"""
    
    def __init__(self):
        # Surface cache sistemi
        self.surface_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Durum renkleri
        self.state_colors = {
            'wandering': (100, 100, 100),   # Gri
            'hunting': (255, 100, 100),     # Kırmızı
            'fleeing': (100, 100, 255),     # Mavi
            'reproducing': (255, 100, 255), # Magenta
        }
        
        # Enerji renkleri
        self.energy_colors = {
            'high': (0, 255, 0),      # Yeşil
            'medium': (255, 255, 0),  # Sarı
            'low': (255, 100, 0),     # Turuncu
            'critical': (255, 0, 0),  # Kırmızı
        }
        
        # Genetik tabanlı renk haritası
        self.gene_color_mapping = {
            'aggression': {
                'low': (0, 255, 0),      # Yeşil (barışçıl)
                'medium': (255, 255, 0),  # Sarı (nötr)
                'high': (255, 0, 0)      # Kırmızı (saldırgan)
            },
            'energy_efficiency': {
                'low': (255, 0, 0),      # Kırmızı (verimsiz)
                'medium': (255, 255, 0),  # Sarı (orta)
                'high': (0, 255, 0)      # Yeşil (verimli)
            },
            'vision_range': {
                'low': (255, 0, 0),      # Kırmızı (kısa görüş)
                'medium': (255, 255, 0),  # Sarı (orta görüş)
                'high': (0, 0, 255)      # Mavi (uzun görüş)
            },
            'speed': {
                'low': (255, 0, 0),      # Kırmızı (yavaş)
                'medium': (255, 255, 0),  # Sarı (orta hız)
                'high': (0, 255, 255)    # Cyan (hızlı)
            }
        }
        
        # Aura efektleri
        self.aura_colors = {
            'energy': (0, 255, 0, 50),      # Yeşil aura (enerji)
            'aggression': (255, 0, 0, 50),  # Kırmızı aura (saldırganlık)
            'social': (0, 0, 255, 50),      # Mavi aura (sosyal)
            'reproduction': (255, 0, 255, 50) # Magenta aura (üreme)
        }
        
        # Davranış ikonları (basit geometrik şekiller)
        self.behavior_icons = {
            'hunting': 'triangle',     # Üçgen (ok)
            'fleeing': 'diamond',      # Elmas (kaçış)
            'reproducing': 'star',     # Yıldız (üreme)
            'wandering': 'circle',     # Daire (dolaşma)
        }
        
        logger.info("🎨 OrganismRenderer oluşturuldu")
    
    def _get_gene_based_color(self, organism) -> Tuple[int, int, int]:
        """Organizmanın genlerine göre renk hesapla"""
        genes = organism.dna.genes
        
        # Agresyon rengi (ana renk)
        aggression = genes.get('aggression', 0.5)
        if aggression < 0.3:
            aggr_color = self.gene_color_mapping['aggression']['low']
        elif aggression < 0.7:
            aggr_color = self.gene_color_mapping['aggression']['medium']
        else:
            aggr_color = self.gene_color_mapping['aggression']['high']
        
        # Enerji verimliliği rengi (ikincil renk)
        efficiency = genes.get('energy_efficiency', 1.0)
        if efficiency < 0.7:
            eff_color = self.gene_color_mapping['energy_efficiency']['low']
        elif efficiency < 1.3:
            eff_color = self.gene_color_mapping['energy_efficiency']['medium']
        else:
            eff_color = self.gene_color_mapping['energy_efficiency']['high']
        
        # Görüş menzili rengi (üçüncül renk)
        vision = genes.get('vision_range', 120.0)
        if vision < 80:
            vision_color = self.gene_color_mapping['vision_range']['low']
        elif vision < 160:
            vision_color = self.gene_color_mapping['vision_range']['medium']
        else:
            vision_color = self.gene_color_mapping['vision_range']['high']
        
        # Renkleri karıştır (ağırlıklı ortalama)
        final_color = (
            int(aggr_color[0] * 0.5 + eff_color[0] * 0.3 + vision_color[0] * 0.2),
            int(aggr_color[1] * 0.5 + eff_color[1] * 0.3 + vision_color[1] * 0.2),
            int(aggr_color[2] * 0.5 + eff_color[2] * 0.3 + vision_color[2] * 0.2)
        )
        
        return final_color
    
    def _draw_aura_effect(self, screen: pygame.Surface, x: int, y: int, size: int, organism):
        """Organizmanın etrafına aura efekti çiz"""
        genes = organism.dna.genes
        
        # Aura boyutu
        aura_size = size + 8
        
        # Enerji aurası (her zaman)
        energy_alpha = min(255, int(organism.energy * 2.5))
        energy_surface = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(energy_surface, (0, 255, 0, energy_alpha), (aura_size, aura_size), aura_size, 2)
        screen.blit(energy_surface, (x - aura_size, y - aura_size))
        
        # Saldırganlık aurası (yüksek agresyon)
        if genes.get('aggression', 0.5) > 0.7:
            aggr_surface = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(aggr_surface, (255, 0, 0, 30), (aura_size, aura_size), aura_size + 4, 1)
            screen.blit(aggr_surface, (x - aura_size, y - aura_size))
        
        # Sosyal aurası (yüksek sosyal çekim)
        if genes.get('social_attraction', 0.3) > 0.6:
            social_surface = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(social_surface, (0, 0, 255, 25), (aura_size, aura_size), aura_size + 6, 1)
            screen.blit(social_surface, (x - aura_size, y - aura_size))
        
        # Üreme aurası (üreme eşiğine yakın)
        if organism.energy >= organism.dna.genes.get('reproduction_threshold', 80.0) * 0.8:
            repro_surface = pygame.Surface((aura_size * 2, aura_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(repro_surface, (255, 0, 255, 40), (aura_size, aura_size), aura_size + 2, 2)
            screen.blit(repro_surface, (x - aura_size, y - aura_size))
    
    def _draw_simple_dot(self, screen: pygame.Surface, x: int, y: int, color: Tuple[int, int, int]):
        """Çok uzak mesafede sadece nokta çiz"""
        pygame.draw.circle(screen, color, (x, y), 1)
    
    def _draw_simple_circle(self, screen: pygame.Surface, x: int, y: int, 
                           color: Tuple[int, int, int], state: str):
        """Uzak mesafede basit daire çiz"""
        size = 2
        pygame.draw.circle(screen, color, (x, y), size)
        
        # Durum rengi ile küçük border
        state_color = self.state_colors.get(state, (100, 100, 100))
        pygame.draw.circle(screen, state_color, (x, y), size + 1, 1)
    
    def draw_organism(self, screen: pygame.Surface, organism, camera, 
                     show_details: bool = True, show_energy: bool = True):
        """Organizmayı çiz (genişletilmiş)"""
        # Dünya koordinatlarını ekran koordinatlarına çevir
        screen_pos = camera.world_to_screen(organism.position)
        screen_x, screen_y = int(screen_pos[0]), int(screen_pos[1])
        
        # Ekran dışındaysa çizme (frustum culling)
        if screen_x < -50 or screen_x > screen.get_width() + 50 or \
           screen_y < -50 or screen_y > screen.get_height() + 50:
            return
        
        # Zoom seviyesine göre LOD (Level of Detail)
        zoom_level = camera.zoom_level
        if zoom_level < 0.5:
            # Çok uzak: Sadece küçük nokta
            gene_color = self._get_gene_based_color(organism)
            self._draw_simple_dot(screen, screen_x, screen_y, gene_color)
            return
        elif zoom_level < 1.0:
            # Uzak: Basit daire
            gene_color = self._get_gene_based_color(organism)
            self._draw_simple_circle(screen, screen_x, screen_y, gene_color, organism.state)
            return
        
        # Temel boyut hesaplama (görsel kalite iyileştirildi)
        base_size = max(6, int(organism.size * camera.zoom_level * 2.0))
        
        # Genetik tabanlı renk
        gene_color = self._get_gene_based_color(organism)
        
        # Durum rengi (daha belirgin)
        state_color = self.state_colors.get(organism.state, (100, 100, 100))
        # Durum rengini daha parlak yap
        state_color = tuple(min(255, c + 50) for c in state_color)
        
        # Enerji rengi (basitleştirilmiş)
        energy_ratio = organism.energy / 100.0
        if energy_ratio > 0.6:
            energy_color = self.energy_colors['high']
        elif energy_ratio > 0.3:
            energy_color = self.energy_colors['medium']
        else:
            energy_color = self.energy_colors['low']
        
        # Aura efekti (zoom yeterliyse)
        if zoom_level > 1.5:
            self._draw_aura_effect(screen, screen_x, screen_y, base_size, organism)
        
        # Ana organizma çizimi
        self._draw_organism_body(screen, screen_x, screen_y, base_size, 
                               gene_color, state_color, organism.state)
        
        # Enerji çubuğu (sadece gerekirse)
        if show_energy and energy_ratio < 0.8:
            self._draw_energy_bar(screen, screen_x, screen_y, base_size, energy_ratio, energy_color)
        
        # Detaylı bilgiler (zoom yüksekse ve performans izin veriyorsa)
        if show_details and camera.zoom_level > 2.0:
            self._draw_organism_details(screen, screen_x, screen_y, base_size, organism)
        
        # Davranış ikonu (sadece önemli durumlarda)
        if camera.zoom_level > 1.0 and organism.state != 'wandering':
            self._draw_behavior_icon(screen, screen_x, screen_y, base_size, organism.state)
        
        # Genetik bilgi etiketi (çok yakın zoom)
        if camera.zoom_level > 3.0:
            self._draw_genetic_info(screen, screen_x, screen_y, base_size, organism)
    
    def _draw_organism_body(self, screen: pygame.Surface, x: int, y: int, size: int, 
                          base_color: Tuple[int, int, int], state_color: Tuple[int, int, int], 
                          state: str):
        """Organizmanın ana gövdesini çiz (profesyonel görünüm)"""
        # Gölge efekti (koyu gri)
        shadow_size = size + 2
        shadow_color = (20, 20, 20)
        pygame.draw.circle(screen, shadow_color, (x + 2, y + 2), shadow_size)
        
        # Ana gövde (gradient efekti için)
        pygame.draw.circle(screen, base_color, (x, y), size)
        
        # İç parlaklık efekti
        highlight_size = max(2, size // 3)
        highlight_color = tuple(min(255, c + 50) for c in base_color)
        pygame.draw.circle(screen, highlight_color, (x - highlight_size//2, y - highlight_size//2), highlight_size)
        
        # Durum halkası (daha belirgin)
        border_size = max(3, size // 3)
        pygame.draw.circle(screen, state_color, (x, y), size + border_size, border_size)
        
        # İç detay (göz efekti - daha büyük)
        eye_size = max(2, size // 4)
        pygame.draw.circle(screen, (255, 255, 255), (x - eye_size, y - eye_size), eye_size)
        pygame.draw.circle(screen, (255, 255, 255), (x + eye_size, y - eye_size), eye_size)
        
        # Göz bebekleri (daha belirgin)
        pupil_size = max(1, eye_size // 2)
        pygame.draw.circle(screen, (0, 0, 0), (x - eye_size, y - eye_size), pupil_size)
        pygame.draw.circle(screen, (0, 0, 0), (x + eye_size, y - eye_size), pupil_size)
        
        # Ağız efekti (küçük çizgi)
        mouth_y = y + eye_size
        pygame.draw.line(screen, (0, 0, 0), (x - eye_size//2, mouth_y), (x + eye_size//2, mouth_y), 1)
    
    def _draw_energy_bar(self, screen: pygame.Surface, x: int, y: int, size: int, 
                        energy_ratio: float, energy_color: Tuple[int, int, int]):
        """Enerji çubuğunu çiz"""
        bar_width = size * 2
        bar_height = max(3, size // 3)
        bar_x = x - bar_width // 2
        bar_y = y - size - bar_height - 5
        
        # Arka plan
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Enerji seviyesi
        energy_width = int(bar_width * energy_ratio)
        if energy_width > 0:
            pygame.draw.rect(screen, energy_color, (bar_x, bar_y, energy_width, bar_height))
        
        # Çerçeve
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)
    
    def _draw_organism_details(self, screen: pygame.Surface, x: int, y: int, size: int, organism):
        """Organizma detaylarını çiz"""
        font = pygame.font.Font(None, max(12, size))
        
        # ID
        id_text = font.render(f"#{organism.organism_id}", True, (255, 255, 255))
        screen.blit(id_text, (x + size + 5, y - size - 15))
        
        # Enerji değeri
        energy_text = font.render(f"{int(organism.energy)}", True, (255, 255, 0))
        screen.blit(energy_text, (x + size + 5, y - size))
        
        # Yaş
        age_text = font.render(f"Age: {int(organism.age)}", True, (200, 200, 200))
        screen.blit(age_text, (x + size + 5, y - size + 15))
    
    def _draw_genetic_info(self, screen: pygame.Surface, x: int, y: int, size: int, organism):
        """Genetik bilgileri çiz"""
        font = pygame.font.Font(None, max(10, size // 2))
        genes = organism.dna.genes
        
        # Önemli genleri göster
        important_genes = ['aggression', 'energy_efficiency', 'vision_range', 'speed']
        y_offset = y + size + 20
        
        for i, gene_name in enumerate(important_genes):
            if gene_name in genes:
                value = genes[gene_name]
                text = f"{gene_name}: {value:.1f}"
                text_surface = font.render(text, True, (200, 200, 200))
                screen.blit(text_surface, (x + size + 5, y_offset + i * 12))
    
    def _draw_behavior_icon(self, screen: pygame.Surface, x: int, y: int, size: int, state: str):
        """Davranış ikonunu çiz"""
        icon_size = max(3, size // 4)
        icon_color = (255, 255, 255)
        
        if state == 'hunting':
            # Üçgen (ok)
            points = [
                (x, y - size - icon_size - 5),
                (x - icon_size, y - size - 5),
                (x + icon_size, y - size - 5)
            ]
            pygame.draw.polygon(screen, icon_color, points)
            
        elif state == 'fleeing':
            # Elmas (kaçış)
            points = [
                (x, y - size - icon_size - 5),
                (x - icon_size, y - size - 5),
                (x, y - size + icon_size - 5),
                (x + icon_size, y - size - 5)
            ]
            pygame.draw.polygon(screen, icon_color, points)
            
        elif state == 'reproducing':
            # Yıldız (üreme)
            center_x, center_y = x, y - size - icon_size - 5
            for i in range(5):
                angle = i * 2 * np.pi / 5
                point_x = center_x + int(icon_size * np.cos(angle))
                point_y = center_y + int(icon_size * np.sin(angle))
                pygame.draw.circle(screen, icon_color, (point_x, point_y), 2)
    
    def get_organism_info(self, organism) -> Dict[str, Any]:
        """Organizma hakkında görsel bilgi döndür"""
        return {
            'id': organism.organism_id,
            'state': organism.state,
            'energy': organism.energy,
            'age': organism.age,
            'color': organism.color,
            'gene_color': self._get_gene_based_color(organism),
            'size': organism.size,
            'position': organism.position.tolist(),
            'fitness': organism.get_fitness(),
            'stats': organism.stats,
            'genes': organism.dna.genes
        } 