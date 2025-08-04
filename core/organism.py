"""
Ecosim Organism - Genetik Yapıya Sahip Canlı Sistemi
"""

import numpy as np
import random
from typing import Dict, List, Optional, Tuple, Any
from .utils import (
    calculate_distance, 
    calculate_angle,
    log_organism_event,
    perf_monitor,
    logger
)

class DNA:
    """Organizmanın genetik yapısını temsil eden sınıf"""
    
    def __init__(self, genes: Optional[Dict[str, float]] = None, species_traits: Optional[Dict[str, Any]] = None):
        """
        Args:
            genes: Gen adı -> değer eşleştirmesi
            species_traits: Tür özellikleri (species_config'dan)
        """
        # Varsayılan genler - TÜR BAZLI
        self.genes = {
            'speed': 25.0,          # Dengeli hareket hızı
            'vision_range': 120.0,  # Optimize görme alanı
            'energy_efficiency': 1.0, # Enerji verimliliği
            'reproduction_threshold': 80.0, # Daha yüksek üreme eşiği - GERÇEKÇİ
            'mutation_rate': 0.1,   # Mutasyon oranı
            'aggression': 0.3,      # Daha az saldırganlık
            'size': random.uniform(1.2, 4.0),  # Boyut varyasyonu daha da artırıldı
            'color_r': random.uniform(0.1, 0.9),  # Daha geniş renk varyasyonu
            'color_g': random.uniform(0.1, 0.9),
            'color_b': random.uniform(0.1, 0.9),
            'lifespan': 100.0,     # Daha kısa yaşam süresi - GERÇEKÇİ
            'metabolism': 0.08,    # Daha yüksek metabolizma - GERÇEKÇİ
            'social_attraction': 0.3, # Daha az sosyal çekim
            'exploration_tendency': 0.6, # Dengeli keşif eğilimi
        }
        
        # Tür özelliklerini uygula
        if species_traits:
            # Tür bazlı özellikleri güncelle
            trait_mapping = {
                'speed': 'speed',
                'vision_range': 'vision_range',
                'metabolism': 'metabolism',
                'aggression': 'aggression',
                'reproduction_threshold': 'reproduction_threshold',
                'energy_efficiency': 'energy_efficiency',
                'social_attraction': 'social_attraction',
                'exploration_tendency': 'exploration_tendency',
                'lifespan': 'lifespan',
                'size': 'size',
                'color_r': 'color_r',
                'color_g': 'color_g',
                'color_b': 'color_b'
            }
            
            for trait_key, gene_key in trait_mapping.items():
                if trait_key in species_traits:
                    self.genes[gene_key] = species_traits[trait_key]
        
        # Eğer genler verilmişse, varsayılanları güncelle
        if genes:
            self.genes.update(genes)
    
    def mutate(self, mutation_rate: float = 0.1, mutation_strength: float = 0.2):
        """DNA'yı mutasyona uğrat"""
        mutated_genes = self.genes.copy()
        
        for gene_name in mutated_genes:
            if random.random() < mutation_rate:
                # Normal dağılım ile mutasyon
                mutation = np.random.normal(0, mutation_strength)
                mutated_genes[gene_name] += mutation
                
                # Değerleri mantıklı sınırlar içinde tut
                mutated_genes[gene_name] = max(0.1, mutated_genes[gene_name])
                
                # Özel sınırlar
                if gene_name in ['color_r', 'color_g', 'color_b']:
                    mutated_genes[gene_name] = max(0.0, min(1.0, mutated_genes[gene_name]))
                elif gene_name == 'mutation_rate':
                    mutated_genes[gene_name] = max(0.01, min(0.5, mutated_genes[gene_name]))
        
        return DNA(mutated_genes)
    
    def crossover(self, other_dna: 'DNA') -> 'DNA':
        """İki DNA'yı çaprazla"""
        new_genes = {}
        
        for gene_name in self.genes:
            if random.random() < 0.5:
                new_genes[gene_name] = self.genes[gene_name]
            else:
                new_genes[gene_name] = other_dna.genes[gene_name]
        
        return DNA(new_genes)
    
    def get_color(self) -> Tuple[int, int, int]:
        """RGB renk değerini döndür"""
        r = int(self.genes['color_r'] * 255)
        g = int(self.genes['color_g'] * 255)
        b = int(self.genes['color_b'] * 255)
        return (r, g, b)

class Organism:
    """Genetik yapıya sahip organizma sınıfı"""
    
    def __init__(self, position: np.ndarray, dna: Optional[DNA] = None, 
                 organism_id: Optional[int] = None, species: Optional[str] = None,
                 species_traits: Optional[Dict[str, Any]] = None):
        """
        Args:
            position: Başlangıç pozisyonu
            dna: Genetik yapı (None ise rastgele oluşturulur)
            organism_id: Organizma kimliği
            species: Tür adı
            species_traits: Tür özellikleri
        """
        self.organism_id = organism_id or random.randint(1000, 9999)
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array([0.0, 0.0], dtype=np.float32)
        
        # Tür bilgileri
        self.species = species or 'unknown'
        self.species_traits = species_traits or {}
        self.diet_type = species_traits.get('diet_type', 'omnivore') if species_traits else 'omnivore'
        
        # DNA'yı tür özellikleriyle oluştur
        self.dna = dna or DNA(species_traits=species_traits)
        
        # Fiziksel özellikler
        self.energy = 100.0
        self.age = 0
        self.size = self.dna.genes['size']
        self.color = self.dna.get_color()
        
        # Davranış durumu - TÜR BAZLI
        self.state = 'wandering'  # wandering, hunting, fleeing, reproducing, resting
        self.behavior_state = 'idle'  # idle, searching_food, chasing_prey, resting, socializing
        self.target_position = None
        self.target_organism = None
        self.target_food = None
        
        # Sosyal özellikler
        self.social_group = None
        self.relationships = {}  # diğer organizmalarla ilişkiler
        
        # İstatistikler
        self.stats = {
            'food_eaten': 0,
            'offspring_count': 0,
            'distance_traveled': 0.0,
            'lifespan': 0,
            'cause_of_death': None,
            'species': self.species,
            'diet_type': self.diet_type
        }
        
        # Performans için
        self.last_update_time = 0
        self.update_interval = 1.0 / 60.0  # 60 FPS
        
        # Üreme kontrolü için
        self.last_reproduction_time = 0
        self.reproduction_cooldown = 10.0  # 10 saniye bekleme süresi
        
        logger.debug(f"🦠 {self.species} #{self.organism_id} oluşturuldu: {position}")
    
    def update(self, world, delta_time: float, frame: int):
        """Organizmayı güncelle"""
        perf_monitor.start_timer(f'organism_update_{self.organism_id}')
        
        try:
            # Yaş ve enerji güncelleme
            self.age += delta_time
            # Hem metabolism hem de energy_decay kullan
            energy_decay = getattr(world, 'energy_decay', 0.08)  # Config'den al
            self.energy -= (self.dna.genes['metabolism'] + energy_decay) * delta_time
            
            # Ölüm kontrolü
            if self.energy <= 0 or self.age >= self.dna.genes['lifespan']:
                cause = 'starvation' if self.energy <= 0 else 'old_age'
                self.die(world, cause, frame)
                return False
            
            # Performans izleme - enerji kritik seviyede
            if self.energy < 20.0 and self.state != 'hunting':
                logger.debug(f"Organism {self.organism_id}: Low energy ({self.energy:.1f}), should hunt")
            
            # Davranış güncelleme
            self._update_behavior(world, delta_time)
            
            # Hareket güncelleme
            self._update_movement(delta_time)
            
            # Dünya sınırları kontrolü
            self._check_world_bounds(world)
            
            # İstatistik güncelleme
            self.stats['lifespan'] = self.age
            
            perf_monitor.end_timer(f'organism_update_{self.organism_id}')
            return True
            
        except Exception as e:
            logger.error(f"Organism #{self.organism_id} güncellenirken hata: {e}")
            return False
    
    def _update_behavior(self, world, delta_time: float):
        """Davranış durumunu güncelle - TÜR BAZLI"""
        # Yakındaki organizmaları ve yiyecekleri bul
        nearby_organisms = world.get_nearby_organisms(
            self.position, 
            self.dna.genes['vision_range']
        )
        nearby_food_indices = world.get_nearby_foods(
            self.position, 
            self.dna.genes['vision_range']
        )
        
        # Davranış durumunu güncelle
        self._update_behavior_state()
        

        

        
        # Durum makinesi - TÜR BAZLI
        if self.behavior_state == 'idle':
            self._idle_behavior(delta_time)
            
            # Yiyecek arama
            if nearby_food_indices:
                self.behavior_state = 'searching_food'
                self.target_food = nearby_food_indices[0]
            
            # Sosyal etkileşim
            if nearby_organisms and self.dna.genes['social_attraction'] > 0.3:
                self._social_interaction(nearby_organisms, world)
        
        elif self.behavior_state == 'reproducing':
            # Üreme durumunda da yemek arayabilir
            if nearby_food_indices:
                self.behavior_state = 'searching_food'
                self.target_food = nearby_food_indices[0]
            else:
                self._reproduction_behavior(world)
        
        elif self.behavior_state == 'searching_food':
            if self.target_food is not None and self.target_food < len(world.foods):
                food = world.foods[self.target_food]
                if food is not None:
                    self._hunt_food(food, world)
                else:
                    self.behavior_state = 'idle'
                    self.target_food = None
            else:
                # Eğer target_food yoksa, yakındaki yiyeceklerden birini seç
                if nearby_food_indices:
                    self.target_food = nearby_food_indices[0]
                else:
                    self.behavior_state = 'idle'
                    self.target_food = None
        
        elif self.behavior_state == 'chasing_prey':
            self._chase_prey_behavior(world, delta_time)
        
        elif self.behavior_state == 'resting':
            self._resting_behavior(delta_time)
        
        elif self.behavior_state == 'socializing':
            self._socializing_behavior(world, delta_time)
        
        # Eski durum makinesi (geriye uyumluluk için) - SADECE YENİ SİSTEM ÇALIŞMAZSA
        if self.behavior_state == 'idle' and self.state == 'wandering':
            self._wander_behavior(delta_time)
        elif self.behavior_state == 'idle' and self.state == 'hunting':
            if self.target_food is not None and self.target_food < len(world.foods):
                food = world.foods[self.target_food]
                if food is not None:
                    self._hunt_food(food, world)
                else:
                    self.state = 'wandering'
                    self.target_food = None
            else:
                self.state = 'wandering'
                self.target_food = None
        elif self.state == 'fleeing':
            self._flee_behavior(delta_time)
            if random.random() < 0.01:
                self.state = 'wandering'
        elif self.state == 'reproducing':
            self._reproduction_behavior(world)
    
    def _wander_behavior(self, delta_time: float):
        """Rastgele dolaşma davranışı"""
        # Keşif eğilimi ve rastgele hareket - daha sık yön değiştirme
        if random.random() < self.dna.genes['exploration_tendency'] * 0.3:
            # Yeni rastgele yön
            angle = random.uniform(0, 2 * np.pi)
            speed = self.dna.genes['speed']
            self.velocity = np.array([
                np.cos(angle) * speed,
                np.sin(angle) * speed
            ])
        
        # Eğer hız çok düşükse, rastgele hareket başlat
        if np.linalg.norm(self.velocity) < 5.0:
            angle = random.uniform(0, 2 * np.pi)
            speed = self.dna.genes['speed']
            self.velocity = np.array([
                np.cos(angle) * speed,
                np.sin(angle) * speed
            ])
    
    def _hunt_food(self, food, world):
        """Yiyecek avlama davranışı"""
        if food is None:
            return
        
        # Yiyeceğe doğru hareket
        direction = food.position - self.position
        distance = np.linalg.norm(direction)
        
        if distance < 15.0:  # Daha geniş yeme mesafesi - GERÇEKÇİ
            # Yiyeceği ye
            self.energy += food.energy_value
            self.stats['food_eaten'] += 1
            
            # Global istatistikleri güncelle
            if hasattr(world, 'stats'):
                world.stats['total_food_eaten'] += 1
            
            # Yiyeceği dünyadan kaldır - DÜZELTİLDİ
            # target_food zaten doğru indeks
            if self.target_food is not None:
                world.remove_food(self.target_food)
            
            # Durumu güncelle
            self.state = 'wandering'
            self.behavior_state = 'idle'
            self.target_food = None
            
            log_organism_event(
                self.organism_id, 
                'ate_food', 
                0,  # frame bilgisi sonra eklenecek
                energy_gained=food.energy_value,
                new_energy=self.energy
            )
        
        else:
            # Yiyeceğe doğru hareket
            direction = direction / distance
            speed = self.dna.genes['speed']
            self.velocity = direction * speed
    
    def _social_interaction(self, nearby_organisms: List[int], world):
        """Sosyal etkileşim davranışı"""
        if not nearby_organisms:
            return
        
        # En yakın organizmayı bul
        closest_org = None
        min_distance = float('inf')
        
        for org_index in nearby_organisms:
            if org_index < len(world.organisms):
                org = world.organisms[org_index]
                if org is not None and org != self:
                    distance = calculate_distance(self.position, org.position)
                    if distance < min_distance:
                        min_distance = distance
                        closest_org = org
        
        if closest_org:
            # Saldırganlık kontrolü
            if (self.dna.genes['aggression'] > 0.7 and 
                closest_org.dna.genes['aggression'] < 0.3):
                # Saldırgan davranış
                self.state = 'fleeing'
                self.target_organism = closest_org
            elif (self.dna.genes['social_attraction'] > 0.6 and 
                  closest_org.dna.genes['social_attraction'] > 0.6):
                # Sosyal çekim
                self._move_towards(closest_org.position)
    
    def _update_behavior_state(self):
        """Davranış durumunu enerji seviyesine göre güncelle"""
        if self.energy > self.dna.genes['reproduction_threshold']:
            self.behavior_state = 'reproducing'
        elif self.energy < 90:  # Çok düşük eşik - yemek arama
            self.behavior_state = 'searching_food'
        elif self.energy < 95:  # Çok düşük eşik - idle
            self.behavior_state = 'idle'
        else:
            self.behavior_state = 'idle'
    
    def _idle_behavior(self, delta_time: float):
        """Boşta kalma davranışı"""
        # Yavaş hareket veya dinlenme
        if random.random() < 0.1:  # %10 şans
            angle = random.uniform(0, 2 * np.pi)
            speed = self.dna.genes['speed'] * 0.3  # Yavaş hareket
            self.velocity = np.array([
                np.cos(angle) * speed,
                np.sin(angle) * speed
            ])
    
    def _chase_prey_behavior(self, world, delta_time: float):
        """Av peşinde koşma davranışı (etçiller için)"""
        if self.diet_type != 'carnivore':
            self.behavior_state = 'idle'
            return
        
        # Yakındaki avları bul
        nearby_organisms = world.get_nearby_organisms(
            self.position, 
            self.dna.genes['vision_range']
        )
        
        if not nearby_organisms:
            self.behavior_state = 'idle'
            return
        
        # En yakın avı bul
        closest_prey = None
        min_distance = float('inf')
        
        for org_index in nearby_organisms:
            if org_index < len(world.organisms):
                org = world.organisms[org_index]
                if org is not None and org != self and org.diet_type == 'herbivore':
                    distance = np.linalg.norm(org.position - self.position)
                    if distance < min_distance:
                        min_distance = distance
                        closest_prey = org
        
        if closest_prey:
            # Avı takip et
            direction = closest_prey.position - self.position
            distance = np.linalg.norm(direction)
            
            if distance < 20.0:  # Yakın mesafe
                # Avı ye
                self.energy += 50.0  # Av yeme enerjisi
                self.stats['food_eaten'] += 1
                
                # Avı öldür
                closest_prey.die(world, 'predation', 0)
                
                self.behavior_state = 'idle'
            else:
                # Avı takip et
                direction = direction / distance
                speed = self.dna.genes['speed'] * 1.2  # Av peşinde daha hızlı
                self.velocity = direction * speed
        else:
            self.behavior_state = 'idle'
    
    def _resting_behavior(self, delta_time: float):
        """Dinlenme davranışı"""
        # Hızı azalt
        self.velocity *= 0.8
        
        # Enerji tüketimini azalt
        self.energy -= self.dna.genes['metabolism'] * delta_time * 0.5
        
        # Belirli süre sonra normal davranışa dön
        if random.random() < 0.05:  # %5 şans
            self.behavior_state = 'idle'
    
    def _socializing_behavior(self, world, delta_time: float):
        """Sosyalleşme davranışı"""
        # Yakındaki aynı türden organizmaları bul
        nearby_organisms = world.get_nearby_organisms(
            self.position, 
            self.dna.genes['vision_range'] * 0.5
        )
        
        if not nearby_organisms:
            self.behavior_state = 'idle'
            return
        
        # Aynı türden organizma bul
        for org_index in nearby_organisms:
            if org_index < len(world.organisms):
                org = world.organisms[org_index]
                if org is not None and org != self and org.species == self.species:
                    # Sosyal etkileşim
                    self._move_towards(org.position)
                    return
        
        self.behavior_state = 'idle'
    
    def _flee_behavior(self, delta_time: float):
        """Kaçma davranışı"""
        if self.target_organism:
            # Hedef organizmadan uzaklaş
            direction = self.position - self.target_organism.position
            direction = direction / np.linalg.norm(direction)
            speed = self.dna.genes['speed'] * 1.5  # Kaçarken daha hızlı
            self.velocity = direction * speed
    
    def _reproduction_behavior(self, world):
        """Üreme davranışı - DENGELİ"""
        if (self.age > 10 and  # 8'den 10'a artırıldı
            self.energy > self.dna.genes['reproduction_threshold'] and
            random.random() < 0.03):  # 0.05'ten 0.03'e düşürüldü
            
            # Enerji maliyeti
            self.energy *= 0.7  # 0.6'dan 0.7'ye artırıldı
            
            # Yeni organizma oluştur
            child_position = self.position + np.random.uniform(-20, 20, 2)
            child = Organism(position=child_position, parent=self)
            world.add_organism(child)
            
            # İstatistikleri güncelle
            world.stats['total_organisms_created'] += 1
            
            log_organism_event(
                self.organism_id,
                'reproduced',
                0,  # frame bilgisi sonra eklenecek
                offspring_id=child.organism_id,
                energy_cost=self.energy * 0.3,
                parent_energy=self.energy
            )
        
        self.state = 'wandering'
    
    def _move_towards(self, target_position: np.ndarray):
        """Hedef pozisyona doğru hareket"""
        direction = target_position - self.position
        distance = np.linalg.norm(direction)
        
        if distance > 0:
            direction = direction / distance
            speed = self.dna.genes['speed']
            self.velocity = direction * speed
    
    def _update_movement(self, delta_time: float):
        """Hareket güncelleme"""
        # Pozisyonu güncelle
        new_position = self.position + self.velocity * delta_time
        
        # Pozisyonu geçerli aralıkta tut
        new_position = np.clip(new_position, 0, 2000)  # Dünya boyutuna göre
        
        self.position = new_position
        
        # Kat edilen mesafeyi kaydet
        self.stats['distance_traveled'] += np.linalg.norm(self.velocity * delta_time)
    
    def _check_world_bounds(self, world):
        """Dünya sınırları kontrolü"""
        bounds_min, bounds_max = world.get_world_bounds()
        
        # Pozisyonu sınırlar içinde tut
        self.position = np.clip(self.position, bounds_min, bounds_max)
        
        # X sınırları - sınırda sek
        if self.position[0] <= bounds_min[0] or self.position[0] >= bounds_max[0]:
            self.velocity[0] *= -0.5
            self.position[0] = np.clip(self.position[0], bounds_min[0], bounds_max[0])
        
        # Y sınırları - sınırda sek
        if self.position[1] <= bounds_min[1] or self.position[1] >= bounds_max[1]:
            self.velocity[1] *= -0.5
            self.position[1] = np.clip(self.position[1], bounds_min[1], bounds_max[1])
    
    def reproduce(self, world) -> Optional['Organism']:
        """Yeni organizma üret"""
        try:
            # Üreme pozisyonu (mevcut pozisyonun yakınında)
            offset = np.random.uniform(-10, 10, 2)
            offspring_position = self.position + offset
            
            # Pozisyonu dünya sınırları içinde tut
            offspring_position = np.clip(offspring_position, 0, 2000)
            
            # Yeni DNA oluştur (mutasyon ile)
            offspring_dna = self.dna.mutate(
                mutation_rate=self.dna.genes['mutation_rate'],
                mutation_strength=0.1
            )
            
            # Yeni organizma oluştur
            offspring = Organism(
                position=offspring_position,
                dna=offspring_dna
            )
            
            log_organism_event(
                self.organism_id,
                'reproduced',
                0,  # frame bilgisi sonra eklenecek
                offspring_id=offspring.organism_id
            )
            
            return offspring
            
        except Exception as e:
            logger.error(f"Üreme sırasında hata: {e}")
            return None
    
    def die(self, world, cause: str, frame: int):
        """Organizmanın ölümü"""
        self.stats['cause_of_death'] = cause
        
        log_organism_event(
            self.organism_id,
            'died',
            frame,
            cause=cause,
            age=self.age,
            energy=self.energy,
            offspring_count=self.stats['offspring_count']
        )
        
        # Dünyadan kaldır
        for i, org in enumerate(world.organisms):
            if org == self:
                world.remove_organism(i)
                break
    
    def get_fitness(self) -> float:
        """Organizmanın uygunluk skorunu hesapla - OPTİMİZE EDİLDİ"""
        # Dengeli uygunluk hesaplama
        food_fitness = self.stats['food_eaten'] * 5.0  # Yiyecek ağırlığı azaltıldı
        reproduction_fitness = self.stats['offspring_count'] * 20.0  # Üreme ağırlığı azaltıldı
        age_fitness = min(self.age * 0.5, 50.0)  # Yaş sınırı
        energy_fitness = min(self.energy * 0.1, 20.0)  # Enerji sınırı
        
        fitness = food_fitness + reproduction_fitness + age_fitness + energy_fitness
        return min(fitness, 100.0)  # Maksimum sınır
    
    def get_info(self) -> Dict[str, Any]:
        """Organizma hakkında bilgi döndür"""
        return {
            'id': self.organism_id,
            'position': self.position.tolist(),
            'energy': self.energy,
            'age': self.age,
            'state': self.state,
            'dna': self.dna.genes,
            'stats': self.stats,
            'fitness': self.get_fitness()
        } 