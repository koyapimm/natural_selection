"""
UI Görselleştirme Sistemi
"""

import pygame
from typing import Dict, Any, List, Tuple, Optional
from core.utils import logger

class UIRenderer:
    """Kullanıcı arayüzünü görselleştiren sınıf"""
    
    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_size = screen_size
        self.width, self.height = screen_size
        
        # Fontlar
        self.title_font = pygame.font.Font(None, 36)
        self.header_font = pygame.font.Font(None, 24)
        self.normal_font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 14)
        self.tiny_font = pygame.font.Font(None, 12)
        
        # Renkler
        self.colors = {
            'background': (20, 20, 20, 180),  # Yarı şeffaf siyah
            'panel': (40, 40, 40, 200),
            'text': (255, 255, 255),
            'text_secondary': (200, 200, 200),
            'accent': (0, 255, 255),
            'warning': (255, 255, 0),
            'danger': (255, 100, 100),
            'success': (100, 255, 100),
            'info': (100, 150, 255),
        }
        
        # Panel boyutları
        self.panel_width = 300
        self.panel_height = 200
        self.margin = 10
        
        # Seçili organizma
        self.selected_organism = None
        self.organism_detail_panel = None
        
        # HUD ayarları
        self.show_hud = True
        self.show_organism_labels = True
        self.show_debug_info = False
        
        logger.info("🖥️ UIRenderer oluşturuldu")
    
    def set_selected_organism(self, organism):
        """Seçili organizmayı ayarla"""
        self.selected_organism = organism
        if organism:
            self.organism_detail_panel = self._create_organism_detail_panel(organism)
    
    def _create_organism_detail_panel(self, organism) -> Dict[str, Any]:
        """Organizma detay paneli oluştur"""
        return {
            'organism': organism,
            'genes': organism.dna.genes,
            'stats': organism.stats,
            'fitness': organism.get_fitness(),
            'position': organism.position.tolist(),
            'energy': organism.energy,
            'age': organism.age,
            'state': organism.state
        }
    
    def draw_main_ui(self, screen: pygame.Surface, simulation_stats: Dict[str, Any], 
                    camera_info: Dict[str, Any], performance_stats: Dict[str, Any]):
        """Ana UI'yi çiz"""
        # Sol üst panel - Temel bilgiler
        self._draw_basic_info_panel(screen, simulation_stats, camera_info)
        
        # Sağ üst panel - İstatistikler
        self._draw_statistics_panel(screen, simulation_stats)
        
        # Sol alt panel - Performans
        self._draw_performance_panel(screen, performance_stats)
        
        # Sağ alt panel - Kontroller
        self._draw_controls_panel(screen)
        
        # Organizma detay paneli (seçili organizma varsa)
        if self.selected_organism and self.organism_detail_panel:
            self._draw_organism_detail_panel(screen)
        
        # Alt bilgi çubuğu
        self._draw_status_bar(screen, simulation_stats)
        
        # HUD paneli
        if self.show_hud:
            self._draw_hud_panel(screen, simulation_stats, camera_info)
    
    def draw_organism_labels(self, screen: pygame.Surface, organisms: List, camera, 
                           zoom_level: float):
        """Organizmaların üzerine etiketler çiz"""
        if not self.show_organism_labels or zoom_level < 2.0:
            return
        
        for organism in organisms:
            if organism is None:
                continue
            
            # Ekran koordinatlarına çevir
            screen_pos = camera.world_to_screen(organism.position)
            screen_x, screen_y = int(screen_pos[0]), int(screen_pos[1])
            
            # Ekran dışındaysa çizme
            if screen_x < 0 or screen_x > self.width or screen_y < 0 or screen_y > self.height:
                continue
            
            # Zoom seviyesine göre etiket içeriği
            if zoom_level > 4.0:
                # Detaylı etiket
                self._draw_detailed_organism_label(screen, organism, screen_x, screen_y)
            elif zoom_level > 2.5:
                # Orta detay etiket
                self._draw_medium_organism_label(screen, organism, screen_x, screen_y)
            else:
                # Basit etiket
                self._draw_simple_organism_label(screen, organism, screen_x, screen_y)
    
    def _draw_simple_organism_label(self, screen: pygame.Surface, organism, x: int, y: int):
        """Basit organizma etiketi"""
        # ID
        id_text = f"#{organism.organism_id}"
        text_surface = self.tiny_font.render(id_text, True, self.colors['text'])
        
        # Arka plan
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.bottom = y - 15
        
        # Yarı şeffaf arka plan
        bg_surface = pygame.Surface((text_rect.width + 4, text_rect.height + 2))
        bg_surface.set_alpha(150)
        bg_surface.fill((0, 0, 0))
        screen.blit(bg_surface, (text_rect.x - 2, text_rect.y - 1))
        
        screen.blit(text_surface, text_rect)
    
    def _draw_medium_organism_label(self, screen: pygame.Surface, organism, x: int, y: int):
        """Orta detay organizma etiketi"""
        # Enerji ve yaş
        energy_text = f"E:{int(organism.energy)}"
        age_text = f"A:{int(organism.age)}"
        
        energy_surface = self.tiny_font.render(energy_text, True, self.colors['text'])
        age_surface = self.tiny_font.render(age_text, True, self.colors['text_secondary'])
        
        # Pozisyonlar
        energy_rect = energy_surface.get_rect()
        age_rect = age_surface.get_rect()
        
        energy_rect.centerx = x
        energy_rect.bottom = y - 20
        
        age_rect.centerx = x
        age_rect.bottom = y - 8
        
        # Arka plan
        bg_width = max(energy_rect.width, age_rect.width) + 4
        bg_height = energy_rect.height + age_rect.height + 4
        bg_surface = pygame.Surface((bg_width, bg_height))
        bg_surface.set_alpha(150)
        bg_surface.fill((0, 0, 0))
        screen.blit(bg_surface, (energy_rect.x - 2, energy_rect.y - 1))
        
        screen.blit(energy_surface, energy_rect)
        screen.blit(age_surface, age_rect)
    
    def _draw_detailed_organism_label(self, screen: pygame.Surface, organism, x: int, y: int):
        """Detaylı organizma etiketi"""
        # Çoklu bilgi satırı
        lines = [
            f"ID: #{organism.organism_id}",
            f"Enerji: {int(organism.energy)}",
            f"Yaş: {int(organism.age)}",
            f"Durum: {organism.state}",
            f"Uygunluk: {organism.get_fitness():.1f}"
        ]
        
        # En uzun satırı bul
        max_width = 0
        text_surfaces = []
        for line in lines:
            surface = self.tiny_font.render(line, True, self.colors['text'])
            text_surfaces.append(surface)
            max_width = max(max_width, surface.get_width())
        
        # Arka plan
        bg_height = len(lines) * 12 + 4
        bg_surface = pygame.Surface((max_width + 8, bg_height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        
        bg_rect = bg_surface.get_rect()
        bg_rect.centerx = x
        bg_rect.bottom = y - 25
        
        screen.blit(bg_surface, bg_rect)
        
        # Metinleri çiz
        for i, surface in enumerate(text_surfaces):
            text_rect = surface.get_rect()
            text_rect.left = bg_rect.left + 4
            text_rect.top = bg_rect.top + 2 + i * 12
            screen.blit(surface, text_rect)
    
    def _draw_hud_panel(self, screen: pygame.Surface, stats: Dict[str, Any], camera_info: Dict[str, Any]):
        """HUD paneli çiz"""
        hud_width = 250
        hud_height = 120
        hud_x = self.width - hud_width - 20
        hud_y = 20
        
        # HUD arka planı
        hud_surface = pygame.Surface((hud_width, hud_height))
        hud_surface.set_alpha(200)
        hud_surface.fill((20, 20, 20))
        screen.blit(hud_surface, (hud_x, hud_y))
        
        # HUD çerçevesi
        pygame.draw.rect(screen, self.colors['accent'], (hud_x, hud_y, hud_width, hud_height), 2)
        
        # HUD başlığı
        title = self.header_font.render("HUD", True, self.colors['accent'])
        screen.blit(title, (hud_x + 10, hud_y + 5))
        
        # HUD içeriği
        y_offset = 35
        hud_lines = [
            f"FPS: {stats.get('fps', 0):.1f}",
            f"Popülasyon: {stats.get('population', 0)}",
            f"Zoom: {camera_info.get('zoom_level', 1.0):.2f}",
            f"Pozisyon: ({camera_info.get('position', [0, 0])[0]:.0f}, {camera_info.get('position', [0, 0])[1]:.0f})",
            f"Chunk Sayısı: {stats.get('chunk_count', 0)}"
        ]
        
        for line in hud_lines:
            text = self.small_font.render(line, True, self.colors['text'])
            screen.blit(text, (hud_x + 10, hud_y + y_offset))
            y_offset += 16
    
    def _draw_organism_detail_panel(self, screen: pygame.Surface):
        """Organizma detay panelini çiz - TÜR BAZLI"""
        if not self.organism_detail_panel:
            return
        
        panel_width = 380
        panel_height = 450
        panel_x = self.width - panel_width - 20
        panel_y = 150
        
        # Panel arka planı
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(220)
        panel_surface.fill((30, 30, 30))
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Panel çerçevesi
        pygame.draw.rect(screen, self.colors['accent'], (panel_x, panel_y, panel_width, panel_height), 2)
        
        org = self.organism_detail_panel['organism']
        genes = self.organism_detail_panel['genes']
        stats = self.organism_detail_panel['stats']
        
        # Başlık - Tür bilgisi ile
        species_name = getattr(org, 'species', 'Bilinmeyen')
        species_display_name = getattr(org, 'species_traits', {}).get('name', species_name)
        title = self.header_font.render(f"{species_display_name} Detayları", True, self.colors['accent'])
        screen.blit(title, (panel_x + 10, panel_y + 10))
        
        # Tür bilgileri
        y_offset = 40
        diet_type = getattr(org, 'diet_type', 'omnivore')
        diet_color = (0, 255, 0) if diet_type == 'herbivore' else (255, 0, 0) if diet_type == 'carnivore' else (255, 255, 0)
        
        diet_text = f"Beslenme: {diet_type}"
        diet_surface = self.normal_font.render(diet_text, True, diet_color)
        screen.blit(diet_surface, (panel_x + 10, panel_y + y_offset))
        y_offset += 25
        
        # Davranış durumu
        behavior_state = getattr(org, 'behavior_state', org.state)
        behavior_text = f"Davranış: {behavior_state}"
        behavior_surface = self.normal_font.render(behavior_text, True, self.colors['text'])
        screen.blit(behavior_surface, (panel_x + 10, panel_y + y_offset))
        y_offset += 25
        
        # Temel bilgiler
        basic_info = [
            f"ID: #{org.organism_id}",
            f"Durum: {org.state}",
            f"Enerji: {int(org.energy)}/100",
            f"Yaş: {int(org.age)}",
            f"Uygunluk: {org.get_fitness():.1f}",
            f"Pozisyon: ({org.position[0]:.0f}, {org.position[1]:.0f})"
        ]
        
        for info in basic_info:
            text = self.normal_font.render(info, True, self.colors['text'])
            screen.blit(text, (panel_x + 10, panel_y + y_offset))
            y_offset += 25
        
        # İstatistikler
        y_offset += 10
        stats_title = self.normal_font.render("İstatistikler:", True, self.colors['accent'])
        screen.blit(stats_title, (panel_x + 10, panel_y + y_offset))
        y_offset += 25
        
        stat_info = [
            f"Yenilen Yiyecek: {stats.get('food_eaten', 0)}",
            f"Yavru Sayısı: {stats.get('offspring_count', 0)}",
            f"Kat Edilen Mesafe: {stats.get('distance_traveled', 0):.1f}",
            f"Yaşam Süresi: {stats.get('lifespan', 0):.1f}"
        ]
        
        for stat in stat_info:
            text = self.small_font.render(stat, True, self.colors['text_secondary'])
            screen.blit(text, (panel_x + 20, panel_y + y_offset))
            y_offset += 20
        
        # Genler
        y_offset += 10
        genes_title = self.normal_font.render("Genetik Yapı:", True, self.colors['accent'])
        screen.blit(genes_title, (panel_x + 10, panel_y + y_offset))
        y_offset += 25
        
        important_genes = ['speed', 'vision_range', 'energy_efficiency', 'aggression', 
                          'reproduction_threshold', 'metabolism', 'social_attraction']
        
        for gene_name in important_genes:
            if gene_name in genes:
                value = genes[gene_name]
                text = f"{gene_name}: {value:.2f}"
                text_surface = self.small_font.render(text, True, self.colors['text_secondary'])
                screen.blit(text_surface, (panel_x + 20, panel_y + y_offset))
                y_offset += 18
    
    def _draw_basic_info_panel(self, screen: pygame.Surface, stats: Dict[str, Any], 
                              camera_info: Dict[str, Any]):
        """Temel bilgi panelini çiz"""
        panel_rect = pygame.Rect(self.margin, self.margin, self.panel_width, self.panel_height)
        
        # Panel arka planı
        self._draw_panel_background(screen, panel_rect)
        
        # Başlık
        title = self.title_font.render("Ecosim", True, self.colors['accent'])
        screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Temel bilgiler
        y_offset = 60
        info_lines = [
            f"FPS: {stats.get('fps', 0):.1f}",
            f"Frame: {stats.get('frame_count', 0)}",
            f"Zaman: {stats.get('current_time', 0):.1f}s",
            f"Zoom: {camera_info.get('zoom_level', 1.0):.2f}",
            f"Pozisyon: ({camera_info.get('position', [0, 0])[0]:.0f}, {camera_info.get('position', [0, 0])[1]:.0f})"
        ]
        
        for line in info_lines:
            text = self.normal_font.render(line, True, self.colors['text'])
            screen.blit(text, (panel_rect.x + 10, panel_rect.y + y_offset))
            y_offset += 25
    
    def _draw_statistics_panel(self, screen: pygame.Surface, stats: Dict[str, Any]):
        """İstatistik panelini çiz"""
        panel_rect = pygame.Rect(self.width - self.panel_width - self.margin, self.margin, 
                               self.panel_width, self.panel_height)
        
        # Panel arka planı
        self._draw_panel_background(screen, panel_rect)
        
        # Başlık
        title = self.header_font.render("İstatistikler", True, self.colors['accent'])
        screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # İstatistikler
        y_offset = 50
        stat_lines = [
            f"Organizmalar: {stats.get('population', 0)}",
            f"Yiyecekler: {stats.get('food_count', 0)}",
            f"Ortalama Uygunluk: {stats.get('average_fitness', 0):.1f}",
            f"Toplam Oluşturulan: {stats.get('total_created', 0)}",
            f"Toplam Ölen: {stats.get('total_died', 0)}",
            f"Toplam Yiyecek: {stats.get('total_food_spawned', 0)}"
        ]
        
        for line in stat_lines:
            text = self.normal_font.render(line, True, self.colors['text'])
            screen.blit(text, (panel_rect.x + 10, panel_rect.y + y_offset))
            y_offset += 22
    
    def _draw_performance_panel(self, screen: pygame.Surface, perf_stats: Dict[str, Any]):
        """Performans panelini çiz"""
        panel_rect = pygame.Rect(self.margin, self.height - self.panel_height - self.margin, 
                               self.panel_width, self.panel_height)
        
        # Panel arka planı
        self._draw_panel_background(screen, panel_rect)
        
        # Başlık
        title = self.header_font.render("Performans", True, self.colors['accent'])
        screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Performans metrikleri
        y_offset = 50
        perf_lines = [
            f"Render: {perf_stats.get('render_time', 0):.3f}ms",
            f"Update: {perf_stats.get('update_time', 0):.3f}ms",
            f"Organizma Update: {perf_stats.get('organism_update_time', 0):.3f}ms",
            f"Yiyecek Update: {perf_stats.get('food_update_time', 0):.3f}ms",
            f"Görünür Organizmalar: {perf_stats.get('visible_organisms', 0)}",
            f"Görünür Yiyecekler: {perf_stats.get('visible_foods', 0)}"
        ]
        
        for line in perf_lines:
            text = self.normal_font.render(line, True, self.colors['text'])
            screen.blit(text, (panel_rect.x + 10, panel_rect.y + y_offset))
            y_offset += 22
    
    def _draw_controls_panel(self, screen: pygame.Surface):
        """Kontrol panelini çiz"""
        panel_rect = pygame.Rect(self.width - self.panel_width - self.margin, 
                               self.height - self.panel_height - self.margin, 
                               self.panel_width, self.panel_height)
        
        # Panel arka planı
        self._draw_panel_background(screen, panel_rect)
        
        # Başlık
        title = self.header_font.render("Kontroller", True, self.colors['accent'])
        screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Kontrol bilgileri
        y_offset = 50
        control_lines = [
            "WASD: Kamera Hareketi",
            "Mouse Wheel: Zoom",
            "Mouse Drag: Kamera Sürükle",
            "Space: Duraklat/Devam",
            "R: Simülasyonu Sıfırla",
            "ESC: Çıkış",
            "F: Tam Ekran"
        ]
        
        for line in control_lines:
            text = self.normal_font.render(line, True, self.colors['text_secondary'])
            screen.blit(text, (panel_rect.x + 10, panel_rect.y + y_offset))
            y_offset += 22
    
    def _draw_status_bar(self, screen: pygame.Surface, stats: Dict[str, Any]):
        """Durum çubuğunu çiz"""
        bar_height = 30
        bar_rect = pygame.Rect(0, self.height - bar_height, self.width, bar_height)
        
        # Arka plan
        pygame.draw.rect(screen, self.colors['background'], bar_rect)
        
        # Durum bilgisi
        status_text = f"Ecosim v1.0 | FPS: {stats.get('fps', 0):.1f} | Organizmalar: {stats.get('population', 0)} | Yiyecekler: {stats.get('food_count', 0)}"
        text = self.small_font.render(status_text, True, self.colors['text'])
        screen.blit(text, (10, self.height - bar_height + 8))
        
        # FPS göstergesi
        fps = stats.get('fps', 0)
        if fps < 20:
            fps_color = self.colors['danger']
        elif fps < 30:
            fps_color = self.colors['warning']
        else:
            fps_color = self.colors['success']
        
        fps_text = f"FPS: {fps:.1f}"
        fps_surface = self.small_font.render(fps_text, True, fps_color)
        fps_rect = fps_surface.get_rect()
        fps_rect.right = self.width - 10
        fps_rect.centery = self.height - bar_height // 2
        screen.blit(fps_surface, fps_rect)
    
    def _draw_panel_background(self, screen: pygame.Surface, rect: pygame.Rect):
        """Panel arka planını çiz"""
        # Yarı şeffaf arka plan
        background_surface = pygame.Surface((rect.width, rect.height))
        background_surface.set_alpha(200)
        background_surface.fill(self.colors['background'])
        screen.blit(background_surface, rect)
        
        # Çerçeve
        pygame.draw.rect(screen, self.colors['accent'], rect, 2)
    
    def draw_popup_message(self, screen: pygame.Surface, message: str, message_type: str = "info"):
        """Popup mesaj çiz"""
        # Mesaj rengi
        if message_type == "warning":
            color = self.colors['warning']
        elif message_type == "error":
            color = self.colors['danger']
        elif message_type == "success":
            color = self.colors['success']
        else:
            color = self.colors['accent']
        
        # Mesaj yüzeyi
        text_surface = self.header_font.render(message, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.width // 2, self.height // 2)
        
        # Arka plan
        padding = 20
        background_rect = text_rect.inflate(padding * 2, padding * 2)
        pygame.draw.rect(screen, self.colors['background'], background_rect)
        pygame.draw.rect(screen, color, background_rect, 2)
        
        # Metin
        screen.blit(text_surface, text_rect)
    
    def draw_mini_map(self, screen: pygame.Surface, world_size: Tuple[int, int], 
                     camera_position: Tuple[float, float], organisms: List, foods: List):
        """Mini harita çiz"""
        map_size = 150
        map_margin = 10
        map_rect = pygame.Rect(self.width - map_size - map_margin, 
                              self.height - map_size - map_margin, map_size, map_size)
        
        # Harita arka planı
        pygame.draw.rect(screen, self.colors['background'], map_rect)
        pygame.draw.rect(screen, self.colors['accent'], map_rect, 2)
        
        # Harita başlığı
        title = self.small_font.render("Mini Harita", True, self.colors['accent'])
        screen.blit(title, (map_rect.x + 5, map_rect.y + 5))
        
        # Organizmaları çiz
        for organism in organisms:
            if organism is not None:
                # Harita koordinatlarına çevir
                map_x = map_rect.x + 10 + (organism.position[0] / world_size[0]) * (map_size - 20)
                map_y = map_rect.y + 25 + (organism.position[1] / world_size[1]) * (map_size - 35)
                
                # Organizma noktası
                pygame.draw.circle(screen, organism.color, (int(map_x), int(map_y)), 2)
        
        # Yiyecekleri çiz
        for food in foods:
            if food is not None:
                map_x = map_rect.x + 10 + (food.position[0] / world_size[0]) * (map_size - 20)
                map_y = map_rect.y + 25 + (food.position[1] / world_size[1]) * (map_size - 35)
                
                pygame.draw.circle(screen, food.color, (int(map_x), int(map_y)), 1)
        
        # Kamera pozisyonu
        cam_x = map_rect.x + 10 + (camera_position[0] / world_size[0]) * (map_size - 20)
        cam_y = map_rect.y + 25 + (camera_position[1] / world_size[1]) * (map_size - 35)
        
        pygame.draw.circle(screen, (255, 255, 255), (int(cam_x), int(cam_y)), 3)
        pygame.draw.circle(screen, (0, 0, 0), (int(cam_x), int(cam_y)), 3, 1) 