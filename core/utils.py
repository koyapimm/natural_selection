"""
Ecosim Utils - GPU Hızlandırma ve Yardımcı Fonksiyonlar
"""

import numpy as np
import time
import logging
from typing import Tuple, List, Optional
import json
from pathlib import Path

# GPU hızlandırma için CuPy import
try:
    import cupy as cp
    GPU_AVAILABLE = True
    print("🚀 CuPy GPU hızlandırma aktif")
except ImportError:
    GPU_AVAILABLE = False
    print("⚠️  CuPy bulunamadı, CPU modunda çalışılıyor")

# Numba JIT derleme
try:
    from numba import jit, prange
    NUMBA_AVAILABLE = True
    print("⚡ Numba JIT derleme aktif")
except ImportError:
    NUMBA_AVAILABLE = False
    print("⚠️  Numba bulunamadı, standart Python kullanılıyor")

# Logging ayarları
import os
from pathlib import Path

# Log dizinini oluştur
log_dir = Path("data/logs")
log_dir.mkdir(parents=True, exist_ok=True)

# Handle Unicode encoding issues on Windows console
import sys
if sys.platform == 'win32':
    try:
        # Use UTF-8 encoding for console output
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except:
        pass  # Fallback if encoding setup fails

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'simulation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performans izleme sınıfı"""
    
    def __init__(self):
        self.timers = {}
        self.counters = {}
    
    def start_timer(self, name: str):
        """Zamanlayıcı başlat"""
        self.timers[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """Zamanlayıcı bitir ve süreyi döndür"""
        if name in self.timers:
            elapsed = time.time() - self.timers[name]
            logger.debug(f"⏱️  {name}: {elapsed:.4f}s")
            return elapsed
        return 0.0
    
    def increment_counter(self, name: str, value: int = 1):
        """Sayaç artır"""
        self.counters[name] = self.counters.get(name, 0) + value
    
    def get_stats(self) -> dict:
        """İstatistikleri döndür"""
        return {
            'timers': self.timers.copy(),
            'counters': self.counters.copy()
        }

# Global performans monitörü
perf_monitor = PerformanceMonitor()

@jit(nopython=True) if NUMBA_AVAILABLE else lambda f: f
def calculate_distance(pos1: np.ndarray, pos2: np.ndarray) -> float:
    """İki nokta arasındaki Öklid mesafesini hesapla"""
    return np.sqrt(np.sum((pos1 - pos2) ** 2))

@jit(nopython=True) if NUMBA_AVAILABLE else lambda f: f
def calculate_angle(pos1: np.ndarray, pos2: np.ndarray) -> float:
    """İki nokta arasındaki açıyı hesapla"""
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return np.arctan2(dy, dx)

def gpu_array_to_cpu(gpu_array):
    """GPU array'ini CPU'ya taşı"""
    if GPU_AVAILABLE and hasattr(gpu_array, 'get'):
        return gpu_array.get()
    return gpu_array

def cpu_array_to_gpu(cpu_array):
    """CPU array'ini GPU'ya taşı"""
    if GPU_AVAILABLE:
        return cp.asarray(cpu_array)
    return cpu_array

def batch_distance_calculation(positions1: np.ndarray, positions2: np.ndarray) -> np.ndarray:
    """Toplu mesafe hesaplama (GPU hızlandırmalı) - OPTİMİZE EDİLDİ"""
    # Performans moduna göre GPU kullanımı
    if GPU_AVAILABLE and len(positions1) > 100 and len(positions2) > 100:  # Daha yüksek threshold
        try:
            gpu_pos1 = cpu_array_to_gpu(positions1)
            gpu_pos2 = cpu_array_to_gpu(positions2)
            
            # GPU'da vektörel mesafe hesaplama (optimize edilmiş)
            diff = gpu_pos1[:, np.newaxis, :] - gpu_pos2[np.newaxis, :, :]
            distances = cp.sqrt(cp.sum(diff ** 2, axis=2))
            
            result = gpu_array_to_cpu(distances)
            perf_monitor.increment_counter('gpu_distance_calculations', 1)
            return result
        except Exception as e:
            logger.warning(f"GPU hesaplama hatası, CPU'ya geçiliyor: {e}")
            perf_monitor.increment_counter('gpu_errors', 1)
    
    # CPU'da hesaplama (optimize edilmiş)
    if len(positions1) > 0 and len(positions2) > 0:
        diff = positions1[:, np.newaxis, :] - positions2[np.newaxis, :, :]
        distances = np.sqrt(np.sum(diff ** 2, axis=2))
        perf_monitor.increment_counter('cpu_distance_calculations', 1)
        return distances
    return np.array([])

def generate_random_positions(count: int, world_size: Tuple[int, int]) -> np.ndarray:
    """Dünya içinde rastgele pozisyonlar üret"""
    if GPU_AVAILABLE and count > 1000:
        # GPU'da büyük batch'ler için
        gpu_positions = cp.random.uniform(
            low=[0, 0], 
            high=world_size, 
            size=(count, 2)
        )
        return gpu_array_to_cpu(gpu_positions)
    else:
        return np.random.uniform(
            low=[0, 0], 
            high=world_size, 
            size=(count, 2)
        )

def save_simulation_data(data: dict, filename: str):
    """Simülasyon verilerini JSON formatında kaydet"""
    data_dir = Path("data/stats")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = data_dir / f"{filename}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"📊 Veriler kaydedildi: {filepath}")

def load_simulation_data(filename: str) -> dict:
    """Simülasyon verilerini JSON formatından yükle"""
    filepath = Path("data/stats") / f"{filename}.json"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def create_color_gradient(values: np.ndarray, colormap: str = 'viridis') -> np.ndarray:
    """Değer dizisini renk gradyanına dönüştür"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        
        # Normalize değerleri 0-1 arasına
        normalized = (values - values.min()) / (values.max() - values.min() + 1e-8)
        
        # Renk haritası uygula
        cmap = cm.get_cmap(colormap)
        colors = cmap(normalized)
        
        # RGBA'yı RGB'ye dönüştür (0-255 arası)
        rgb_colors = (colors[:, :3] * 255).astype(np.uint8)
        return rgb_colors
        
    except ImportError:
        # Matplotlib yoksa basit renk gradyanı
        normalized = (values - values.min()) / (values.max() - values.min() + 1e-8)
        colors = np.zeros((len(values), 3), dtype=np.uint8)
        colors[:, 0] = (normalized * 255).astype(np.uint8)  # Kırmızı
        colors[:, 1] = ((1 - normalized) * 255).astype(np.uint8)  # Yeşil
        return colors

def log_organism_event(organism_id: int, event_type: str, frame: int, **kwargs):
    """Organizma olaylarını logla"""
    event_data = {
        'organism_id': organism_id,
        'event_type': event_type,
        'frame': frame,
        'timestamp': time.time(),
        **kwargs
    }
    
    logger.info(f"🦠 Organism #{organism_id} {event_type} at frame {frame}")
    
    # JSON log dosyasına da kaydet
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "organism_events.jsonl"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event_data, ensure_ascii=False) + '\n') 