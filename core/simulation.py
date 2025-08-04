"""
Ecosim Simulation - Ana Simülasyon Motoru
"""

import pygame
import numpy as np
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .world import World
from .organism import Organism, DNA
from .food import Food, FoodSpawner
from .camera import Camera
from .species_manager import SpeciesManager
from .utils import (
    generate_random_positions,
    save_simulation_data,
    perf_monitor,
    logger
)
from visuals import OrganismRenderer, FoodRenderer, UIRenderer, CameraOverlay, PerformanceMonitor

class Simulation:
    """Ana simülasyon motoru"""
    
    def __init__(self, config: Dict[str, Any], headless: bool = False):
        """
        Args:
            config: Simülasyon yapılandırması
            headless: Görsel olmadan çalışma modu
        """
        self.config = config
        self.headless = headless
        
        # Simülasyon durumu
        self.running = False
        self.paused = False
        self.frame_count = 0
        self.start_time = time.time()
        self.current_time = 0.0
        
        # FPS ve zaman yönetimi
        self.target_fps = config.get('simulation', {}).get('fps', 60)
        self.frame_time = 1.0 / self.target_fps
        self.last_frame_time = 0.0
        
        # Performans modu ayarları
        self.performance_mode = config.get('simulation', {}).get('performance_mode', 'medium')
        self.debug_mode = config.get('simulation', {}).get('debug_mode', False)
        
        # Performans moduna göre ayarlar
        self._apply_performance_settings()
        
        # Dünya ve sistemler
        world_size = config.get('simulation', {}).get('world_size', [2000, 2000])
        max_organisms = config.get('simulation', {}).get('max_organisms', 2000)
        self.world = World(size=world_size)
        self.world.max_organisms = max_organisms
        
        # Tür yöneticisi
        self.species_manager = SpeciesManager()
        self.world.species_manager = self.species_manager
        
        # Yiyecek sistemi
        food_config = config.get('food', {})
        self.food_spawner = FoodSpawner(world_size, food_config)
        
        # Kamera sistemi (sadece görsel modda)
        if not headless:
            screen_size = config.get('visualization', {}).get('screen_size', [1200, 800])
            self.camera = Camera(screen_size, world_size)
            self._init_pygame(screen_size)
            
            # Görselleştirme sistemleri
            self.organism_renderer = OrganismRenderer()
            self.food_renderer = FoodRenderer()
            self.ui_renderer = UIRenderer(screen_size)
            self.camera_overlay = CameraOverlay(screen_size)
            self.performance_monitor = PerformanceMonitor(debug_mode=self.debug_mode)
        else:
            self.camera = None
            self.screen = None
            self.organism_renderer = None
            self.food_renderer = None
            self.ui_renderer = None
            self.camera_overlay = None
            self.performance_monitor = None
        
        # İstatistikler
        self.stats = {
            'total_organisms_created': 0,
            'total_organisms_died': 0,
            'total_food_spawned': 0,
            'total_food_eaten': 0,
            'generation_count': 0,
            'average_fitness': 0.0,
            'population_history': [],
            'fitness_history': []
        }
        
        # Debug modda performans logları
        if self.debug_mode:
            self.performance_log = []
            logger.info("🔍 Debug modu aktif - performans logları kaydediliyor")
        
        # Başlangıç organizmalarını oluştur
        self._initialize_organisms()
        
        logger.info(f"🎮 Simulation başlatıldı: {world_size}, FPS: {self.target_fps}, Mode: {self.performance_mode}")
    
    def _log_performance_data(self):
        """Debug modda performans verilerini logla"""
        if not self.debug_mode:
            return
            
        perf_stats = perf_monitor.get_stats()
        gpu_stats = {
            'gpu_calculations': perf_stats['counters'].get('gpu_distance_calculations', 0),
            'cpu_calculations': perf_stats['counters'].get('cpu_distance_calculations', 0),
            'gpu_errors': perf_stats['counters'].get('gpu_errors', 0)
        }
        
        log_entry = {
            'frame': self.frame_count,
            'time': self.current_time,
            'fps': self.performance_monitor.metrics.get('fps', 0),
            'frame_time': self.performance_monitor.metrics.get('frame_time', 0),
            'population': len(self.world.organisms),
            'visible_organisms': self.performance_monitor.metrics.get('visible_organisms', 0),
            'gpu_stats': gpu_stats
        }
        
        self.performance_log.append(log_entry)
        
        # Her 100 frame'de bir özet log
        if self.frame_count % 100 == 0:
            logger.info(f"📊 Frame {self.frame_count}: FPS={log_entry['fps']:.1f}, "
                       f"Pop={log_entry['population']}, GPU={gpu_stats['gpu_calculations']}")
    
    def _apply_performance_settings(self):
        """Performans moduna göre ayarları uygula"""
        if self.performance_mode == 'low':
            # Düşük performans modu
            self.max_organisms = 200
            self.update_throttle = 3  # Her 3 frame'de bir güncelle
            self.render_throttle = 2  # Her 2 frame'de bir çiz
            self.show_details = False
            self.show_energy_bars = False
            self.show_grid = False
            logger.info("🔧 Düşük performans modu aktif")
            
        elif self.performance_mode == 'medium':
            # Orta performans modu
            self.max_organisms = 500
            self.update_throttle = 2  # Her 2 frame'de bir güncelle
            self.render_throttle = 1  # Her frame çiz
            self.show_details = True
            self.show_energy_bars = True
            self.show_grid = True
            logger.info("🔧 Orta performans modu aktif")
            
        else:  # high
            # Yüksek performans modu
            self.max_organisms = 1000
            self.update_throttle = 1  # Her frame güncelle
            self.render_throttle = 1  # Her frame çiz
            self.show_details = True
            self.show_energy_bars = True
            self.show_grid = True
            logger.info("🔧 Yüksek performans modu aktif")
    
    def _init_pygame(self, screen_size: Tuple[int, int]):
        """Pygame'i başlat"""
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Ecosim - Evrimsel Biyoloji Simülasyonu")
        self.clock = pygame.time.Clock()
        
        # Font
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def _initialize_organisms(self):
        """Başlangıç organizmalarını oluştur - TÜR BAZLI"""
        organism_config = self.config.get('organism', {})
        initial_count = organism_config.get('initial_count', 100)
        
        # Rastgele pozisyonlar oluştur
        positions = generate_random_positions(initial_count, self.world.size)
        
        for i in range(initial_count):
            # Biome için uygun türde organizma oluştur
            organism = self.world.spawn_organism_for_biome(positions[i])
            if organism:
                self.world.add_organism(organism)
                self.stats['total_organisms_created'] += 1
            else:
                # Fallback: varsayılan organizma
                organism = Organism(position=positions[i])
                self.world.add_organism(organism)
                self.stats['total_organisms_created'] += 1
        
        logger.info(f"🦠 {initial_count} başlangıç organizması oluşturuldu (tür bazlı)")
    
    def run(self, scenario_handler=None):
        """Ana simülasyon döngüsü"""
        self.running = True
        
        try:
            while self.running:
                # Zaman yönetimi
                current_time = time.time()
                delta_time = min(current_time - self.last_frame_time, self.frame_time)
                self.last_frame_time = current_time
                self.current_time += delta_time
                
                # Olayları işle
                if not self.headless:
                    self._handle_events()
                
                # Simülasyonu güncelle
                if not self.paused:
                    self._update(delta_time, scenario_handler)
                
                # Görselleştirme
                if not self.headless:
                    self._render()
                
                # FPS kontrolü
                if not self.headless:
                    self.clock.tick(self.target_fps)
                
                # Frame sayacını artır
                self.frame_count += 1
                
                # İstatistikleri güncelle
                if self.frame_count % 60 == 0:  # Her saniye
                    self._update_statistics()
                
        except KeyboardInterrupt:
            logger.info("Simülasyon kullanıcı tarafından durduruldu")
        except Exception as e:
            logger.error(f"Simülasyon çalışırken hata: {e}")
        finally:
            self.cleanup()
    
    def _render(self):
        """Gelişmiş görselleştirme (throttling ile)"""
        if self.headless:
            return
        
        # Render throttling: Sadece belirli frame'lerde çiz
        if self.frame_count % self.render_throttle != 0:
            return
            
        self.performance_monitor.start_frame()
        perf_monitor.start_timer('rendering')
        
        try:
            # Ekranı temizle
            self.screen.fill((20, 20, 40))  # Koyu mavi arka plan
            
            # Biome zeminini çiz (zoom düşükse)
            if self.camera.zoom_level < 2.0:
                self._draw_biome_background()
            
            # Kamera overlay'leri çiz (grid, koordinatlar) - sadece gerekirse
            if self.show_grid and self.camera.zoom_level < 3.0:  # Zoom düşükse grid çiz
                self.camera_overlay.draw_all_overlays(self.screen, self.camera)
            
            # Görünür organizmaları çiz (optimize edilmiş)
            visible_organisms = self.camera.get_visible_organisms(self.world.organisms)
            visible_organism_count = 0
            
            # Performans için zoom seviyesine göre detay ayarı
            show_details = self.show_details and self.camera.zoom_level > 2.0
            show_energy = self.show_energy_bars and self.camera.zoom_level > 1.0
            
            for org_index in visible_organisms:
                organism = self.world.organisms[org_index]
                if organism is not None:
                    self.organism_renderer.draw_organism(
                        self.screen, organism, self.camera,
                        show_details=show_details,
                        show_energy=show_energy
                    )
                    visible_organism_count += 1
            
            # Organizma etiketlerini çiz
            self.ui_renderer.draw_organism_labels(
                self.screen, self.world.organisms, self.camera, self.camera.zoom_level
            )
            
            # Görünür yiyecekleri çiz (optimize edilmiş)
            visible_foods = self.camera.get_visible_foods(self.world.foods)
            visible_food_count = 0
            
            # Yiyecek detayları sadece yüksek zoom'da
            food_show_details = self.show_details and self.camera.zoom_level > 2.5
            
            for food_index in visible_foods:
                food = self.world.foods[food_index]
                if food is not None:
                    self.food_renderer.draw_food(
                        self.screen, food, self.camera,
                        show_details=food_show_details
                    )
                    visible_food_count += 1
            
            # Performans metriklerini güncelle
            self.performance_monitor.update_metrics(
                visible_organisms=visible_organism_count,
                visible_foods=visible_food_count,
                total_organisms=len(self.world.organisms),
                total_foods=len(self.world.foods)
            )
            
            # Debug modda performans logları
            if self.debug_mode:
                self._log_performance_data()
            
            # UI çiz
            self._draw_enhanced_ui()
            
            # Ekranı güncelle
            pygame.display.flip()
            
            # Performans frame'ini bitir
            self.performance_monitor.end_frame()
            
            perf_monitor.end_timer('rendering')
            
        except Exception as e:
            logger.error(f"Render sırasında hata: {e}")
    
    def _draw_biome_background(self):
        """Biome zeminini çiz"""
        try:
            if not hasattr(self.world, 'biomes'):
                return
            
            # Ekran boyutları
            screen_width, screen_height = self.screen.get_size()
            
            # Görünür alanı hesapla
            visible_area = self.camera.get_visible_area()
            top_left, bottom_right = visible_area
            
            # Biome çözünürlüğü (performans için düşük)
            biome_resolution = max(20, int(50 / self.camera.zoom_level))
            
            for x in range(0, screen_width, biome_resolution):
                for y in range(0, screen_height, biome_resolution):
                    # Ekran koordinatlarını dünya koordinatlarına çevir
                    world_x = top_left[0] + (x / screen_width) * (bottom_right[0] - top_left[0])
                    world_y = top_left[1] + (y / screen_height) * (bottom_right[1] - top_left[1])
                    
                    # Dünya sınırları içinde mi kontrol et
                    if (0 <= world_x < self.world.size[0] and 0 <= world_y < self.world.size[1]):
                        # Biome rengini al
                        biome_color = self.world.get_biome_color_at(world_x, world_y)
                        
                        # Biome rengini biraz koyulaştır
                        darkened_color = tuple(max(0, c - 30) for c in biome_color)
                        
                        # Biome karesini çiz
                        pygame.draw.rect(self.screen, darkened_color, 
                                       (x, y, biome_resolution, biome_resolution))
        except Exception as e:
            logger.error(f"Biome background çizilirken hata: {e}")
            # Hata durumunda sadece geç
            pass
    
    def _handle_events(self):
        """Pygame olaylarını işle (genişletilmiş)"""
        mouse_wheel = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._reset_simulation()
                elif event.key == pygame.K_f:
                    self._toggle_fullscreen()
                elif event.key == pygame.K_h:
                    self.ui_renderer.show_hud = not self.ui_renderer.show_hud
                elif event.key == pygame.K_l:
                    self.ui_renderer.show_organism_labels = not self.ui_renderer.show_organism_labels
            elif event.type == pygame.MOUSEWHEEL:
                mouse_wheel = event.y
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol tık
                    self._handle_mouse_click(event.pos)
        
        # Klavye durumunu al
        keys_pressed = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        # Kamerayı güncelle
        if self.camera:
            self.camera.handle_input(keys_pressed, mouse_pos, mouse_wheel, self.frame_time)
    
    def _handle_mouse_click(self, mouse_pos: Tuple[int, int]):
        """Mouse tıklama olayını işle"""
        # Dünya koordinatlarına çevir
        world_pos = self.camera.screen_to_world(np.array(mouse_pos))
        
        # En yakın organizmayı bul
        closest_organism = None
        min_distance = float('inf')
        
        for organism in self.world.organisms:
            if organism is not None:
                distance = np.linalg.norm(organism.position - world_pos)
                if distance < min_distance and distance < 50:  # 50 piksel mesafe
                    min_distance = distance
                    closest_organism = organism
        
        # Seçili organizmayı ayarla
        self.ui_renderer.set_selected_organism(closest_organism)
        
        if closest_organism:
            logger.info(f"Organizma seçildi: #{closest_organism.organism_id}")
    
    def _toggle_fullscreen(self):
        """Tam ekran modunu değiştir"""
        if not self.headless:
            pygame.display.toggle_fullscreen()
    
    def _update(self, delta_time: float, scenario_handler=None):
        """Simülasyonu güncelle"""
        perf_monitor.start_timer('simulation_update')
        
        try:
            # Senaryo güncellemesi
            if scenario_handler:
                scenario_handler.step(self, delta_time, self.frame_count)
            
            # Yiyecek üretimi
            new_food = self.food_spawner.spawn_food(self.frame_count)
            if new_food:
                self.world.add_food(new_food)
                self.stats['total_food_spawned'] += 1
            
            # Organizmaları güncelle
            self._update_organisms(delta_time)
            
            # Yiyecekleri güncelle
            self._update_foods(delta_time)
            
            # Dünya temizliği
            self.world.cleanup_unused_chunks()
            
            perf_monitor.end_timer('simulation_update')
            
        except Exception as e:
            logger.error(f"Simülasyon güncellenirken hata: {e}")
    
    def _update_organisms(self, delta_time: float):
        """Tüm organizmaları güncelle (throttling ile)"""
        perf_monitor.start_timer('organisms_update')
        
        # Throttling: Sadece belirli frame'lerde güncelle
        if self.frame_count % self.update_throttle == 0:
            # Organizmaları ters sırayla güncelle (silme işlemleri için)
            for i in range(len(self.world.organisms) - 1, -1, -1):
                organism = self.world.organisms[i]
                if organism is not None:
                    # Organizmayı güncelle
                    if not organism.update(self.world, delta_time, self.frame_count):
                        # Organizma öldü
                        self.stats['total_organisms_died'] += 1
                    
                    # Dünya pozisyonunu güncelle
                    self.world.update_organism_position(i, organism.position)
        
        perf_monitor.end_timer('organisms_update')
    
    def _update_foods(self, delta_time: float):
        """Tüm yiyecekleri güncelle"""
        perf_monitor.start_timer('foods_update')
        
        # Yiyecekleri ters sırayla güncelle
        for i in range(len(self.world.foods) - 1, -1, -1):
            food = self.world.foods[i]
            if food is not None:
                if not food.update(delta_time, self.frame_count):
                    # Yiyecek bozuldu
                    self.world.remove_food(i)
        
        perf_monitor.end_timer('foods_update')
    
    def _update_statistics(self):
        """İstatistikleri güncelle"""
        # World stats'ını simulation stats'a kopyala
        self.stats['total_food_eaten'] = self.world.stats.get('total_food_eaten', 0)
        
        # Dünya istatistiklerini güncelle
        world_stats = self.world.get_statistics()
        self.stats['total_organisms_created'] = world_stats.get('total_organisms', 0)
        
        # Popülasyon sayısı
        current_population = len(self.world.organisms)
        self.stats['population_history'].append({
            'frame': self.frame_count,
            'population': current_population,
            'time': self.current_time
        })
        
        # Ortalama uygunluk
        if current_population > 0:
            total_fitness = sum(org.get_fitness() for org in self.world.organisms if org is not None)
            self.stats['average_fitness'] = total_fitness / current_population
            self.stats['fitness_history'].append({
                'frame': self.frame_count,
                'average_fitness': self.stats['average_fitness'],
                'time': self.current_time
            })
        
        # Geçmiş verileri sınırla (performans için)
        max_history = 1000
        if len(self.stats['population_history']) > max_history:
            self.stats['population_history'] = self.stats['population_history'][-max_history:]
        if len(self.stats['fitness_history']) > max_history:
            self.stats['fitness_history'] = self.stats['fitness_history'][-max_history:]
    
    def _draw_organism(self, organism):
        """Organizmayı çiz"""
        # Dünya koordinatlarını ekran koordinatlarına çevir
        screen_pos = self.camera.world_to_screen(organism.position)
        
        # Boyut hesapla
        size = max(2, int(organism.size * self.camera.zoom_level))
        
        # Renk belirle
        color = organism.color
        
        # Enerji seviyesine göre parlaklık
        energy_ratio = organism.energy / 100.0
        brightness = int(128 + energy_ratio * 127)
        color = tuple(min(255, int(c * brightness / 255)) for c in color)
        
        # Organizmayı çiz
        pygame.draw.circle(self.screen, color, 
                          (int(screen_pos[0]), int(screen_pos[1])), size)
        
        # Enerji çubuğu (opsiyonel)
        if self.camera.zoom_level > 2.0:
            bar_width = 20
            bar_height = 3
            bar_x = int(screen_pos[0] - bar_width // 2)
            bar_y = int(screen_pos[1] - size - 10)
            
            # Arka plan
            pygame.draw.rect(self.screen, (50, 50, 50), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Enerji seviyesi
            energy_width = int(bar_width * energy_ratio)
            energy_color = (0, 255, 0) if energy_ratio > 0.5 else (255, 255, 0) if energy_ratio > 0.2 else (255, 0, 0)
            pygame.draw.rect(self.screen, energy_color, 
                           (bar_x, bar_y, energy_width, bar_height))
    
    def _draw_food(self, food):
        """Yiyeceği çiz"""
        # Dünya koordinatlarını ekran koordinatlarına çevir
        screen_pos = self.camera.world_to_screen(food.position)
        
        # Boyut hesapla
        size = max(1, int(food.size * self.camera.zoom_level))
        
        # Yiyeceği çiz
        pygame.draw.circle(self.screen, food.color, 
                          (int(screen_pos[0]), int(screen_pos[1])), size)
    
    def _draw_enhanced_ui(self):
        """Gelişmiş kullanıcı arayüzünü çiz"""
        if self.headless:
            return
            
        # Simülasyon istatistikleri
        simulation_stats = {
            'fps': self.performance_monitor.metrics['fps'],
            'frame_count': self.frame_count,
            'current_time': self.current_time,
            'population': len(self.world.organisms),
            'food_count': len(self.world.foods),
            'average_fitness': self.stats['average_fitness'],
            'total_created': self.stats['total_organisms_created'],
            'total_died': self.stats['total_organisms_died'],
            'total_food_spawned': self.stats['total_food_spawned'],
            'chunk_count': self.world.stats.get('chunk_count', 0)
        }
        
        # Kamera bilgileri
        camera_info = {
            'zoom_level': self.camera.zoom_level,
            'position': self.camera.position
        }
        
        # Performans istatistikleri
        performance_stats = self.performance_monitor.get_performance_stats()
        
        # Ana UI'yi çiz
        self.ui_renderer.draw_main_ui(
            self.screen, simulation_stats, camera_info, performance_stats
        )
        
        # Mini harita çiz
        self.ui_renderer.draw_mini_map(
            self.screen, self.world.size, self.camera.position, 
            self.world.organisms, self.world.foods
        )
    
    def _reset_simulation(self):
        """Simülasyonu sıfırla"""
        logger.info("🔄 Simülasyon sıfırlanıyor...")
        
        # Dünyayı temizle
        self.world.organisms.clear()
        self.world.foods.clear()
        self.world.spatial_hash.clear()
        self.world.chunks.clear()
        self.world.active_chunks.clear()
        
        # İstatistikleri sıfırla
        self.stats = {
            'total_organisms_created': 0,
            'total_organisms_died': 0,
            'total_food_spawned': 0,
            'total_food_eaten': 0,
            'generation_count': 0,
            'average_fitness': 0.0,
            'population_history': [],
            'fitness_history': []
        }
        
        # Kamerayı sıfırla
        if self.camera:
            self.camera.reset_view()
        
        # Yeni organizmalar oluştur
        self._initialize_organisms()
        
        logger.info("✅ Simülasyon sıfırlandı")
    
    def export_results(self):
        """Simülasyon sonuçlarını dışa aktar"""
        try:
            # İstatistikleri hazırla
            export_data = {
                'simulation_info': {
                    'frame_count': self.frame_count,
                    'total_time': self.current_time,
                    'config': self.config
                },
                'statistics': self.stats,
                'world_stats': self.world.get_statistics(),
                'performance_stats': perf_monitor.get_stats()
            }
            
            # Dosyaya kaydet
            timestamp = int(time.time())
            filename = f"simulation_results_{timestamp}"
            save_simulation_data(export_data, filename)
            
            logger.info(f"📊 Simülasyon sonuçları dışa aktarıldı: {filename}")
            
        except Exception as e:
            logger.error(f"Sonuçlar dışa aktarılırken hata: {e}")
    
    def cleanup(self):
        """Simülasyonu temizle"""
        logger.info("🧹 Simülasyon temizleniyor...")
        
        if not self.headless:
            pygame.quit()
        
        # Son istatistikleri kaydet
        self.export_results()
        
        logger.info("✅ Simülasyon temizlendi")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Simülasyon istatistiklerini döndür"""
        return {
            **self.stats,
            'world_stats': self.world.get_statistics(),
            'performance_stats': perf_monitor.get_stats(),
            'current_time': self.current_time,
            'frame_count': self.frame_count
        } 