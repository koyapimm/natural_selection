"""
Ecosim World - Dünya ve Çevre Sistemi
"""

import numpy as np
import random
from typing import Dict, List, Optional, Tuple, Any
from .utils import logger

class Biome:
    """Biome (ekosistem) sınıfı"""
    
    def __init__(self, name: str, color: Tuple[int, int, int], 
                 temperature: float, humidity: float, fertility: float):
        self.name = name
        self.color = color
        self.temperature = temperature  # 0-1 arası
        self.humidity = humidity        # 0-1 arası
        self.fertility = fertility      # 0-1 arası
        
        # Biome özellikleri
        self.food_spawn_rate = fertility * 0.5 + 0.1
        self.organism_energy_cost = (1.0 - fertility) * 0.3 + 0.7

class World:
    """Dünya sistemi - organizmalar ve yiyecekler için ortam"""
    
    def __init__(self, size: Tuple[int, int] = (2000, 2000)):
        self.size = np.array(size, dtype=np.float32)
        
        # Organizmalar ve yiyecekler
        self.organisms = []
        self.foods = []
        
        # Spatial hash sistemi (performans için)
        self.spatial_hash = {}
        self.chunk_size = 100
        self.chunks = {}
        self.active_chunks = set()
        
        # İstatistikler
        self.stats = {
            'total_organisms': 0,
            'total_food_eaten': 0,
            'total_food_spawned': 0,
            'chunk_count': 0
        }
        
        # Perlin noise için seed
        self.noise_seed = random.randint(0, 10000)
        
        # Biome sistemi
        self.biomes = self._initialize_biomes()
        self.biome_noise = self._generate_biome_noise()
        
        # Tür yöneticisi
        self.species_manager = None  # Simulation tarafından set edilecek
        
        # Enerji ayarları
        self.energy_decay = 0.08  # Config'den alınacak
        
        logger.info(f"🌍 World oluşturuldu: {size}")
    
    def _initialize_biomes(self) -> Dict[str, Biome]:
        """Biome'ları başlat"""
        return {
            'forest': Biome('Forest', (34, 139, 34), 0.6, 0.8, 0.9),      # Orman
            'desert': Biome('Desert', (238, 203, 173), 0.9, 0.1, 0.2),    # Çöl
            'tundra': Biome('Tundra', (240, 248, 255), 0.1, 0.3, 0.3),    # Tundra
            'grassland': Biome('Grassland', (144, 238, 144), 0.5, 0.5, 0.7), # Çayır
            'swamp': Biome('Swamp', (139, 69, 19), 0.7, 0.9, 0.6),        # Bataklık
            'mountain': Biome('Mountain', (105, 105, 105), 0.3, 0.4, 0.4), # Dağ
            'ocean': Biome('Ocean', (70, 130, 180), 0.4, 1.0, 0.5),       # Okyanus
        }
    
    def _generate_biome_noise(self) -> np.ndarray:
        """Biome dağılımı için noise oluştur"""
        # Basit Perlin noise benzeri sistem
        width, height = int(self.size[0] // 50), int(self.size[1] // 50)  # Daha az detay
        noise = np.zeros((height, width))
        
        # Çoklu katman noise
        for octave in range(3):
            scale = 2 ** octave
            amplitude = 1.0 / scale
            
            for y in range(height):
                for x in range(width):
                    # Basit hash fonksiyonu
                    nx = x / width
                    ny = y / height
                    
                    # Noise değeri hesapla
                    value = self._simple_noise(nx * scale, ny * scale)
                    noise[y, x] += value * amplitude
        
        return noise
    
    def _simple_noise(self, x: float, y: float) -> float:
        """Basit noise fonksiyonu"""
        # Hash tabanlı noise
        n = int(x * 1000 + y * 1000 + self.noise_seed)
        n = (n << 13) ^ n
        n = (n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff
        return (n / 0x7fffffff) * 2.0 - 1.0
    
    def get_biome_at(self, x: float, y: float) -> Biome:
        """Belirli koordinattaki biome'u döndür"""
        # Noise koordinatlarına çevir
        nx = int(x / 50) % self.biome_noise.shape[1]
        ny = int(y / 50) % self.biome_noise.shape[0]
        
        # Noise değerini al
        noise_value = self.biome_noise[ny, nx]
        
        # Noise değerine göre biome seç
        if noise_value < -0.5:
            return self.biomes['tundra']
        elif noise_value < -0.2:
            return self.biomes['mountain']
        elif noise_value < 0.0:
            return self.biomes['forest']
        elif noise_value < 0.3:
            return self.biomes['grassland']
        elif noise_value < 0.6:
            return self.biomes['swamp']
        elif noise_value < 0.8:
            return self.biomes['desert']
        else:
            return self.biomes['ocean']
    
    def get_biome_color_at(self, x: float, y: float) -> Tuple[int, int, int]:
        """Belirli koordinattaki biome rengini döndür"""
        biome = self.get_biome_at(x, y)
        return biome.color
    
    def get_biome_info_at(self, x: float, y: float) -> Dict[str, Any]:
        """Belirli koordinattaki biome bilgilerini döndür"""
        biome = self.get_biome_at(x, y)
        return {
            'name': biome.name,
            'color': biome.color,
            'temperature': biome.temperature,
            'humidity': biome.humidity,
            'fertility': biome.fertility,
            'food_spawn_rate': biome.food_spawn_rate,
            'organism_energy_cost': biome.organism_energy_cost
        }
    
    def get_world_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Dünya sınırlarını döndür"""
        return np.array([0, 0]), self.size
    
    def add_organism(self, organism):
        """Organizma ekle - NÜFUS KONTROLÜ İLE"""
        # Maksimum nüfus kontrolü (config'den alınacak)
        max_organisms = getattr(self, 'max_organisms', 2000)  # Varsayılan değer
        
        if len(self.organisms) >= max_organisms:
            # En eski organizmayı kaldır (FIFO)
            oldest_organism = None
            oldest_index = -1
            
            for i, org in enumerate(self.organisms):
                if org is not None:
                    if oldest_organism is None or org.age > oldest_organism.age:
                        oldest_organism = org
                        oldest_index = i
            
            if oldest_index >= 0:
                self.remove_organism(oldest_index)
        
        self.organisms.append(organism)
        self.stats['total_organisms'] += 1
        
        # Spatial hash'e ekle
        self._add_to_spatial_hash(organism.position, len(self.organisms) - 1, 'organism')
        
        # Chunk'a ekle
        chunk_key = self._get_chunk_key(organism.position)
        if chunk_key not in self.chunks:
            self.chunks[chunk_key] = {'organisms': [], 'foods': []}
            self.active_chunks.add(chunk_key)
        
        self.chunks[chunk_key]['organisms'].append(len(self.organisms) - 1)
    
    def spawn_organism_for_biome(self, position: np.ndarray) -> Optional['Organism']:
        """Biome için uygun türde organizma oluştur"""
        if self.species_manager is None:
            return None
        
        # Biome'u belirle
        biome = self.get_biome_at(position[0], position[1])
        biome_name = biome.name.lower()
        
        # Uygun tür seç
        species_name = self.species_manager.select_random_species_for_biome(biome_name)
        if not species_name:
            return None
        
        # Tür özelliklerini al
        species_traits = self.species_manager.get_species_traits(species_name)
        
        # Organizma oluştur
        from .organism import Organism
        organism = Organism(
            position=position,
            species=species_name,
            species_traits=species_traits
        )
        
        return organism
    
    def remove_organism(self, index: int):
        """Organizma kaldır"""
        if 0 <= index < len(self.organisms):
            organism = self.organisms[index]
            if organism is not None:
                # Spatial hash'ten kaldır
                self._remove_from_spatial_hash(organism.position, index, 'organism')
                
                # Chunk'tan kaldır
                chunk_key = self._get_chunk_key(organism.position)
                if chunk_key in self.chunks:
                    if index in self.chunks[chunk_key]['organisms']:
                        self.chunks[chunk_key]['organisms'].remove(index)
                
                # Organizmayı None yap (silme işlemi için)
                self.organisms[index] = None
                self.stats['total_organisms'] -= 1
    
    def add_food(self, food):
        """Yiyecek ekle"""
        self.foods.append(food)
        self.stats['total_food_spawned'] += 1
        
        # Spatial hash'e ekle
        self._add_to_spatial_hash(food.position, len(self.foods) - 1, 'food')
        
        # Chunk'a ekle
        chunk_key = self._get_chunk_key(food.position)
        if chunk_key not in self.chunks:
            self.chunks[chunk_key] = {'organisms': [], 'foods': []}
            self.active_chunks.add(chunk_key)
        
        self.chunks[chunk_key]['foods'].append(len(self.foods) - 1)
    
    def remove_food(self, index: int):
        """Yiyecek kaldır"""
        if 0 <= index < len(self.foods):
            food = self.foods[index]
            if food is not None:
                # Spatial hash'ten kaldır
                self._remove_from_spatial_hash(food.position, index, 'food')
                
                # Chunk'tan kaldır
                chunk_key = self._get_chunk_key(food.position)
                if chunk_key in self.chunks:
                    if index in self.chunks[chunk_key]['foods']:
                        self.chunks[chunk_key]['foods'].remove(index)
                
                # Yiyeceği None yap
                self.foods[index] = None
    
    def update_organism_position(self, index: int, new_position: np.ndarray):
        """Organizma pozisyonunu güncelle"""
        if 0 <= index < len(self.organisms):
            organism = self.organisms[index]
            if organism is not None:
                old_position = organism.position.copy()
                organism.position = new_position
                
                # Spatial hash'i güncelle
                self._update_spatial_hash_position(old_position, new_position, index, 'organism')
                
                # Chunk'ları güncelle
                old_chunk = self._get_chunk_key(old_position)
                new_chunk = self._get_chunk_key(new_position)
                
                if old_chunk != new_chunk:
                    # Eski chunk'tan kaldır
                    if old_chunk in self.chunks and index in self.chunks[old_chunk]['organisms']:
                        self.chunks[old_chunk]['organisms'].remove(index)
                    
                    # Yeni chunk'a ekle
                    if new_chunk not in self.chunks:
                        self.chunks[new_chunk] = {'organisms': [], 'foods': []}
                        self.active_chunks.add(new_chunk)
                    
                    self.chunks[new_chunk]['organisms'].append(index)
    
    def get_nearby_organisms(self, position: np.ndarray, radius: float) -> List[int]:
        """Yakındaki organizmaları bul"""
        nearby = []
        
        # Chunk tabanlı arama
        center_chunk = self._get_chunk_key(position)
        chunk_radius = max(1, int(radius / self.chunk_size))
        
        for dx in range(-chunk_radius, chunk_radius + 1):
            for dy in range(-chunk_radius, chunk_radius + 1):
                chunk_key = (center_chunk[0] + dx, center_chunk[1] + dy)
                
                if chunk_key in self.chunks:
                    for org_index in self.chunks[chunk_key]['organisms']:
                        if org_index < len(self.organisms):
                            organism = self.organisms[org_index]
                            if organism is not None:
                                distance = np.linalg.norm(organism.position - position)
                                if distance <= radius:
                                    nearby.append(org_index)
        
        return nearby
    
    def get_nearby_foods(self, position: np.ndarray, radius: float) -> List[int]:
        """Yakındaki yiyecekleri bul"""
        nearby = []
        
        # Chunk tabanlı arama
        center_chunk = self._get_chunk_key(position)
        chunk_radius = max(1, int(radius / self.chunk_size))
        
        for dx in range(-chunk_radius, chunk_radius + 1):
            for dy in range(-chunk_radius, chunk_radius + 1):
                chunk_key = (center_chunk[0] + dx, center_chunk[1] + dy)
                
                if chunk_key in self.chunks:
                    for food_index in self.chunks[chunk_key]['foods']:
                        if food_index < len(self.foods):
                            food = self.foods[food_index]
                            if food is not None:
                                distance = np.linalg.norm(food.position - position)
                                if distance <= radius:
                                    nearby.append(food_index)
        
        return nearby
    
    def _get_chunk_key(self, position: np.ndarray) -> Tuple[int, int]:
        """Pozisyon için chunk anahtarını hesapla"""
        chunk_x = int(position[0] // self.chunk_size)
        chunk_y = int(position[1] // self.chunk_size)
        return (chunk_x, chunk_y)
    
    def _add_to_spatial_hash(self, position: np.ndarray, index: int, entity_type: str):
        """Spatial hash'e ekle"""
        chunk_key = self._get_chunk_key(position)
        if chunk_key not in self.spatial_hash:
            self.spatial_hash[chunk_key] = {'organisms': [], 'foods': []}
        
        self.spatial_hash[chunk_key][f'{entity_type}s'].append(index)
    
    def _remove_from_spatial_hash(self, position: np.ndarray, index: int, entity_type: str):
        """Spatial hash'ten kaldır"""
        chunk_key = self._get_chunk_key(position)
        if chunk_key in self.spatial_hash:
            if index in self.spatial_hash[chunk_key][f'{entity_type}s']:
                self.spatial_hash[chunk_key][f'{entity_type}s'].remove(index)
    
    def _update_spatial_hash_position(self, old_position: np.ndarray, new_position: np.ndarray, 
                                    index: int, entity_type: str):
        """Spatial hash pozisyonunu güncelle"""
        old_chunk = self._get_chunk_key(old_position)
        new_chunk = self._get_chunk_key(new_position)
        
        if old_chunk != new_chunk:
            # Eski chunk'tan kaldır
            if old_chunk in self.spatial_hash:
                if index in self.spatial_hash[old_chunk][f'{entity_type}s']:
                    self.spatial_hash[old_chunk][f'{entity_type}s'].remove(index)
            
            # Yeni chunk'a ekle
            if new_chunk not in self.spatial_hash:
                self.spatial_hash[new_chunk] = {'organisms': [], 'foods': []}
            
            self.spatial_hash[new_chunk][f'{entity_type}s'].append(index)
    
    def cleanup_unused_chunks(self):
        """Kullanılmayan chunk'ları temizle"""
        chunks_to_remove = []
        
        for chunk_key in self.chunks:
            if (len(self.chunks[chunk_key]['organisms']) == 0 and 
                len(self.chunks[chunk_key]['foods']) == 0):
                chunks_to_remove.append(chunk_key)
        
        for chunk_key in chunks_to_remove:
            del self.chunks[chunk_key]
            self.active_chunks.discard(chunk_key)
        
        self.stats['chunk_count'] = len(self.chunks)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Dünya istatistiklerini döndür"""
        return {
            **self.stats,
            'total_organisms': self.stats.get('total_organisms', 0),  # Toplam oluşturulan organizma sayısı
            'active_chunks': len(self.active_chunks),
            'total_chunks': len(self.chunks),
            'organism_count': len([org for org in self.organisms if org is not None]),
            'food_count': len([food for food in self.foods if food is not None])
        } 