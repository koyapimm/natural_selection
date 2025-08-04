"""
Performans İzleme Sistemi
"""

import time
import pygame
from typing import Dict, Any, List
from core.utils import logger, perf_monitor

class PerformanceMonitor:
    """Görselleştirme performansını izleyen sınıf"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.enabled = debug_mode  # Debug modda aktif
        
        self.frame_times = []
        self.max_frame_history = 60  # Son 60 frame'i tut
        
        # Performans metrikleri
        self.metrics = {
            'fps': 0.0,
            'frame_time': 0.0,
            'render_time': 0.0,
            'update_time': 0.0,
            'organism_update_time': 0.0,
            'food_update_time': 0.0,
            'visible_organisms': 0,
            'visible_foods': 0,
            'total_organisms': 0,
            'total_foods': 0,
        }
        
        # Performans uyarıları
        self.warnings = []
        self.last_warning_time = 0
        self.warning_cooldown = 5.0  # 5 saniye
        
        logger.info("⚡ PerformanceMonitor oluşturuldu")
    
    def start_frame(self):
        """Frame başlangıcını işaretle"""
        if not self.enabled:
            return
        self.frame_start_time = time.time()
    
    def end_frame(self):
        """Frame bitişini işaretle ve metrikleri güncelle"""
        if not self.enabled:
            return
            
        frame_time = (time.time() - self.frame_start_time) * 1000  # ms cinsinden
        
        # Frame zamanını kaydet
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.max_frame_history:
            self.frame_times.pop(0)
        
        # FPS hesapla
        if len(self.frame_times) > 1:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.metrics['fps'] = 1000.0 / avg_frame_time if avg_frame_time > 0 else 0
        else:
            self.metrics['fps'] = 1000.0 / frame_time if frame_time > 0 else 0
        
        self.metrics['frame_time'] = frame_time
        
        # Performans kontrolü
        self._check_performance()
    
    def update_metrics(self, **kwargs):
        """Metrikleri güncelle"""
        for key, value in kwargs.items():
            if key in self.metrics:
                self.metrics[key] = value
    
    def _check_performance(self):
        """Performans kontrolü yap"""
        current_time = time.time()
        
        # FPS düşükse uyarı
        if self.metrics['fps'] < 20 and current_time - self.last_warning_time > self.warning_cooldown:
            warning_msg = f"⚠️ Düşük FPS: {self.metrics['fps']:.1f}"
            self.warnings.append({
                'message': warning_msg,
                'time': current_time,
                'type': 'fps_low'
            })
            self.last_warning_time = current_time
            logger.warning(warning_msg)
        
        # Frame time yüksekse uyarı
        if self.metrics['frame_time'] > 50 and current_time - self.last_warning_time > self.warning_cooldown:
            warning_msg = f"⚠️ Yüksek Frame Time: {self.metrics['frame_time']:.1f}ms"
            self.warnings.append({
                'message': warning_msg,
                'time': current_time,
                'type': 'frame_time_high'
            })
            self.last_warning_time = current_time
            logger.warning(warning_msg)
        
        # Eski uyarıları temizle
        self.warnings = [w for w in self.warnings if current_time - w['time'] < 10.0]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Performans istatistiklerini döndür"""
        return {
            'fps': self.metrics['fps'],
            'frame_time': self.metrics['frame_time'],
            'render_time': self.metrics['render_time'],
            'update_time': self.metrics['update_time'],
            'organism_update_time': self.metrics['organism_update_time'],
            'food_update_time': self.metrics['food_update_time'],
            'visible_organisms': self.metrics['visible_organisms'],
            'visible_foods': self.metrics['visible_foods'],
            'total_organisms': self.metrics['total_organisms'],
            'total_foods': self.metrics['total_foods'],
            'avg_frame_time': sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0,
            'min_frame_time': min(self.frame_times) if self.frame_times else 0,
            'max_frame_time': max(self.frame_times) if self.frame_times else 0,
            'warnings': len(self.warnings)
        }
    
    def get_performance_color(self) -> tuple:
        """Performans durumuna göre renk döndür"""
        fps = self.metrics['fps']
        if fps >= 50:
            return (0, 255, 0)  # Yeşil
        elif fps >= 30:
            return (255, 255, 0)  # Sarı
        elif fps >= 20:
            return (255, 165, 0)  # Turuncu
        else:
            return (255, 0, 0)  # Kırmızı
    
    def draw_performance_graph(self, screen: pygame.Surface, x: int, y: int, width: int, height: int):
        """Performans grafiği çiz"""
        if not self.frame_times:
            return
        
        # Grafik arka planı
        pygame.draw.rect(screen, (20, 20, 20), (x, y, width, height))
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height), 1)
        
        # Frame time grafiği
        if len(self.frame_times) > 1:
            max_time = max(self.frame_times)
            min_time = min(self.frame_times)
            time_range = max_time - min_time if max_time != min_time else 1
            
            points = []
            for i, frame_time in enumerate(self.frame_times):
                graph_x = x + (i / len(self.frame_times)) * width
                graph_y = y + height - ((frame_time - min_time) / time_range) * height
                points.append((graph_x, graph_y))
            
            if len(points) > 1:
                pygame.draw.lines(screen, (0, 255, 255), False, points, 2)
        
        # FPS çizgisi (16.67ms = 60 FPS)
        target_fps_y = y + height - (16.67 / max(self.frame_times) if self.frame_times else 1) * height
        pygame.draw.line(screen, (255, 255, 0), (x, target_fps_y), (x + width, target_fps_y), 1)
        
        # FPS metni
        font = pygame.font.Font(None, 16)
        fps_text = font.render(f"FPS: {self.metrics['fps']:.1f}", True, (255, 255, 255))
        screen.blit(fps_text, (x + 5, y + 5))
    
    def log_performance_summary(self):
        """Performans özetini logla"""
        if not self.frame_times:
            return
        
        avg_fps = self.metrics['fps']
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        min_frame_time = min(self.frame_times)
        max_frame_time = max(self.frame_times)
        
        summary = f"""
📊 Performans Özeti:
   FPS: {avg_fps:.1f}
   Ortalama Frame Time: {avg_frame_time:.1f}ms
   Min Frame Time: {min_frame_time:.1f}ms
   Max Frame Time: {max_frame_time:.1f}ms
   Görünür Organizmalar: {self.metrics['visible_organisms']}/{self.metrics['total_organisms']}
   Görünür Yiyecekler: {self.metrics['visible_foods']}/{self.metrics['total_foods']}
        """
        
        logger.info(summary)
        
        # Performans önerileri
        if avg_fps < 30:
            logger.warning("💡 Performans Önerileri:")
            logger.warning("   - Görünür alan dışındaki organizmaları çizme")
            logger.warning("   - Zoom seviyesine göre detay seviyesini azalt")
            logger.warning("   - Organizma sayısını sınırla")
        
        if self.metrics['render_time'] > 20:
            logger.warning("   - Render optimizasyonu gerekli")
        
        if self.metrics['organism_update_time'] > 10:
            logger.warning("   - Organizma update optimizasyonu gerekli") 