"""
Varsayılan Senaryo - Temel Evrimsel Simülasyon
"""

import numpy as np
from typing import Dict, Any

class Scenario:
    """Varsayılan evrimsel simülasyon senaryosu"""
    
    def __init__(self, simulation):
        self.simulation = simulation
        self.name = "Default"
        self.description = "Temel evrimsel simülasyon - doğal seçilim ve mutasyon"
        
        # Senaryo durumu
        self.step_count = 0
        self.last_generation_check = 0
        
        # İstatistikler
        self.generation_stats = {
            'generation_count': 0,
            'best_fitness': 0.0,
            'average_fitness': 0.0,
            'population_size': 0
        }
    
    def init(self):
        """Senaryo başlatma"""
        print("🎭 Varsayılan senaryo başlatıldı")
        print("📊 Bu senaryo temel evrimsel ilkeleri gösterir:")
        print("   - Doğal seçilim")
        print("   - Genetik mutasyon")
        print("   - Popülasyon dinamikleri")
        print("   - Çevresel değişiklikler")
    
    def step(self, simulation, delta_time: float, frame: int):
        """Her adımda çalışacak kod"""
        self.step_count += 1
        
        # Her 1000 adımda bir nesil kontrolü
        if frame - self.last_generation_check >= 1000:
            self._check_generation(simulation, frame)
            self.last_generation_check = frame
        
        # Popülasyon kontrolü
        self._check_population_health(simulation)
        
        # Çevresel değişiklikler
        self._apply_environmental_changes(simulation, frame)
    
    def _check_generation(self, simulation, frame: int):
        """Nesil kontrolü ve istatistikleri"""
        organisms = simulation.world.organisms
        
        if not organisms:
            return
        
        # Uygunluk hesaplamaları
        fitnesses = [org.get_fitness() for org in organisms if org is not None]
        
        if fitnesses:
            self.generation_stats['generation_count'] += 1
            self.generation_stats['best_fitness'] = max(fitnesses)
            self.generation_stats['average_fitness'] = np.mean(fitnesses)
            self.generation_stats['population_size'] = len(organisms)
            
            # İstatistikleri logla
            print(f"📊 Nesil {self.generation_stats['generation_count']}: "
                  f"Popülasyon={len(organisms)}, "
                  f"Ortalama Uygunluk={self.generation_stats['average_fitness']:.1f}, "
                  f"En İyi Uygunluk={self.generation_stats['best_fitness']:.1f}")
    
    def _check_population_health(self, simulation):
        """Popülasyon sağlığını kontrol et"""
        population_size = len(simulation.world.organisms)
        
        # Popülasyon çok düşükse yeni organizmalar ekle
        if population_size < 20:
            self._spawn_emergency_organisms(simulation, 10)
        
        # Popülasyon çok yüksekse yiyecek üretimini artır
        elif population_size > 500:
            simulation.food_spawner.spawn_config['spawn_rate'] = min(
                0.15, 
                simulation.food_spawner.spawn_config.get('spawn_rate', 0.05) + 0.01
            )
    
    def _spawn_emergency_organisms(self, simulation, count: int):
        """Acil durum organizmaları üret"""
        from core.organism import Organism, DNA
        from core.utils import generate_random_positions
        
        positions = generate_random_positions(count, simulation.world.size)
        
        for i in range(count):
            # Çeşitlilik için farklı DNA'lar
            if i % 3 == 0:
                dna = DNA({'speed': 1.5, 'vision_range': 60.0})  # Hızlı avcı
            elif i % 3 == 1:
                dna = DNA({'social_attraction': 0.8, 'exploration_tendency': 0.7})  # Sosyal
            else:
                dna = DNA({'energy_efficiency': 1.3, 'metabolism': 0.8})  # Verimli
            
            organism = Organism(position=positions[i], dna=dna)
            simulation.world.add_organism(organism)
            simulation.stats['total_organisms_created'] += 1
        
        print(f"🆘 Acil durum: {count} yeni organizma eklendi")
    
    def _apply_environmental_changes(self, simulation, frame: int):
        """Çevresel değişiklikleri uygula"""
        # Periyodik değişiklikler
        if frame % 5000 == 0:  # Her 5000 frame'de bir
            # Yiyecek üretim oranını rastgele değiştir
            current_rate = simulation.food_spawner.spawn_config.get('spawn_rate', 0.05)
            new_rate = np.clip(current_rate + np.random.normal(0, 0.02), 0.01, 0.2)
            simulation.food_spawner.spawn_config['spawn_rate'] = new_rate
            
            print(f"🌍 Çevresel değişiklik: Yiyecek üretim oranı {new_rate:.3f}")
        
        # Dünya genişletme
        if frame % 10000 == 0:  # Her 10000 frame'de bir
            directions = ['right', 'left', 'up', 'down']
            direction = np.random.choice(directions)
            amount = np.random.randint(200, 800)
            simulation.world.expand_world(direction, amount)
            
            print(f"🌍 Dünya genişletildi: {direction} yönünde {amount} birim")
    
    def visualize(self, simulation):
        """Görselleştirme özelleştirmeleri"""
        # Bu senaryoda özel görselleştirme yok
        pass
    
    def handle_event(self, event_name: str, event_config: Dict[str, Any], simulation):
        """Özel olayları işle"""
        print(f"🎭 Olay işlendi: {event_name}")
        
        if event_name == "population_boom":
            print("📈 Popülasyon patlaması! Yiyecek üretimi artırıldı.")
        elif event_name == "fitness_peak":
            print("🏆 Uygunluk zirvesi! Yeni agresif organizmalar eklendi.")
        elif event_name == "time_milestone":
            print("⏰ Zaman dönümü! Dünya genişletildi.")
    
    def cleanup(self):
        """Senaryo temizleme"""
        print("🎭 Varsayılan senaryo tamamlandı")
        print(f"📊 Final istatistikler:")
        print(f"   - Toplam adım: {self.step_count}")
        print(f"   - Nesil sayısı: {self.generation_stats['generation_count']}")
        print(f"   - En iyi uygunluk: {self.generation_stats['best_fitness']:.1f}") 