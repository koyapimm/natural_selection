"""
Ecosim ScenarioHandler - Senaryo Yönetim Sistemi
"""

import importlib
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from .utils import logger

class ScenarioHandler:
    """Senaryo yönetim sistemi"""
    
    def __init__(self, scenario_name: str, simulation):
        """
        Args:
            scenario_name: Senaryo adı
            simulation: Simülasyon nesnesi
        """
        self.scenario_name = scenario_name
        self.simulation = simulation
        self.scenario_module = None
        self.scenario_instance = None
        
        # Senaryo yapılandırması
        self.config = {}
        
        # Senaryo durumu
        self.is_loaded = False
        self.is_active = False
        
        # Senaryo istatistikleri
        self.stats = {
            'steps_executed': 0,
            'events_triggered': 0,
            'custom_actions': 0
        }
        
        # Senaryoyu yükle
        self._load_scenario()
        
        logger.info(f"🎭 ScenarioHandler oluşturuldu: {scenario_name}")
    
    def _load_scenario(self):
        """Senaryoyu yükle"""
        try:
            # Senaryo dosya yolunu oluştur
            scenario_path = Path(f"scenarios/{self.scenario_name}")
            scenario_file = scenario_path / "scenario.py"
            
            if not scenario_file.exists():
                logger.warning(f"Senaryo dosyası bulunamadı: {scenario_file}")
                self._create_default_scenario()
                return
            
            # Senaryo modülünü import et
            sys.path.insert(0, str(scenario_path))
            self.scenario_module = importlib.import_module("scenario")
            
            # Senaryo sınıfını al
            if hasattr(self.scenario_module, 'Scenario'):
                scenario_class = self.scenario_module.Scenario
                self.scenario_instance = scenario_class(self.simulation)
                self.is_loaded = True
                
                # Yapılandırmayı yükle
                config_file = scenario_path / "config.yaml"
                if config_file.exists():
                    import yaml
                    with open(config_file, 'r', encoding='utf-8') as f:
                        self.config = yaml.safe_load(f)
                
                logger.info(f"✅ Senaryo yüklendi: {self.scenario_name}")
            else:
                logger.error(f"Senaryo sınıfı bulunamadı: {self.scenario_name}")
                self._create_default_scenario()
                
        except Exception as e:
            logger.error(f"Senaryo yüklenirken hata: {e}")
            self._create_default_scenario()
    
    def _create_default_scenario(self):
        """Varsayılan senaryo oluştur"""
        logger.info("🔧 Varsayılan senaryo oluşturuluyor...")
        
        class DefaultScenario:
            def __init__(self, simulation):
                self.simulation = simulation
                self.name = "Default"
                self.description = "Varsayılan evrimsel simülasyon"
            
            def init(self):
                """Senaryo başlatma"""
                pass
            
            def step(self, simulation, delta_time, frame):
                """Her adımda çalışacak kod"""
                pass
            
            def visualize(self, simulation):
                """Görselleştirme özelleştirmeleri"""
                pass
            
            def cleanup(self):
                """Senaryo temizleme"""
                pass
        
        self.scenario_instance = DefaultScenario(self.simulation)
        self.is_loaded = True
        self.config = {}
    
    def init(self):
        """Senaryoyu başlat"""
        if self.scenario_instance and hasattr(self.scenario_instance, 'init'):
            try:
                self.scenario_instance.init()
                self.is_active = True
                logger.info(f"🎭 Senaryo başlatıldı: {self.scenario_name}")
            except Exception as e:
                logger.error(f"Senaryo başlatılırken hata: {e}")
    
    def step(self, simulation, delta_time: float, frame: int):
        """Senaryo adımını çalıştır"""
        if not self.is_active or not self.scenario_instance:
            return
        
        try:
            # Senaryo adımını çalıştır
            if hasattr(self.scenario_instance, 'step'):
                self.scenario_instance.step(simulation, delta_time, frame)
                self.stats['steps_executed'] += 1
            
            # Özel olayları kontrol et
            self._check_events(simulation, frame)
            
        except Exception as e:
            logger.error(f"Senaryo adımı çalıştırılırken hata: {e}")
    
    def _check_events(self, simulation, frame: int):
        """Özel olayları kontrol et"""
        if not self.config.get('events'):
            return
        
        events = self.config['events']
        
        for event_name, event_config in events.items():
            if self._should_trigger_event(event_config, simulation, frame):
                self._trigger_event(event_name, event_config, simulation)
    
    def _should_trigger_event(self, event_config: Dict, simulation, frame: int) -> bool:
        """Olayın tetiklenip tetiklenmeyeceğini kontrol et"""
        trigger_type = event_config.get('trigger_type', 'frame')
        
        if trigger_type == 'frame':
            trigger_frame = event_config.get('trigger_frame', 0)
            return frame == trigger_frame
        
        elif trigger_type == 'population':
            min_pop = event_config.get('min_population', 0)
            max_pop = event_config.get('max_population', float('inf'))
            current_pop = len(simulation.world.organisms)
            return min_pop <= current_pop <= max_pop
        
        elif trigger_type == 'fitness':
            min_fitness = event_config.get('min_fitness', 0)
            current_fitness = simulation.stats.get('average_fitness', 0)
            return current_fitness >= min_fitness
        
        elif trigger_type == 'time':
            trigger_time = event_config.get('trigger_time', 0)
            return simulation.current_time >= trigger_time
        
        return False
    
    def _trigger_event(self, event_name: str, event_config: Dict, simulation):
        """Olayı tetikle"""
        try:
            action_type = event_config.get('action_type', 'custom')
            
            if action_type == 'spawn_organisms':
                self._spawn_organisms_event(event_config, simulation)
            elif action_type == 'modify_environment':
                self._modify_environment_event(event_config, simulation)
            elif action_type == 'change_parameters':
                self._change_parameters_event(event_config, simulation)
            elif action_type == 'custom':
                self._custom_event(event_name, event_config, simulation)
            
            self.stats['events_triggered'] += 1
            logger.info(f"🎭 Olay tetiklendi: {event_name}")
            
        except Exception as e:
            logger.error(f"Olay tetiklenirken hata: {e}")
    
    def _spawn_organisms_event(self, event_config: Dict, simulation):
        """Organizma üretme olayı"""
        count = event_config.get('count', 10)
        organism_type = event_config.get('organism_type', 'random')
        
        from .organism import Organism, DNA
        from .utils import generate_random_positions
        
        positions = generate_random_positions(count, simulation.world.size)
        
        for i in range(count):
            if organism_type == 'random':
                dna = DNA()
            elif organism_type == 'aggressive':
                dna = DNA({'aggression': 0.8, 'speed': 1.5})
            elif organism_type == 'social':
                dna = DNA({'social_attraction': 0.8, 'exploration_tendency': 0.3})
            else:
                dna = DNA()
            
            organism = Organism(position=positions[i], dna=dna)
            simulation.world.add_organism(organism)
            simulation.stats['total_organisms_created'] += 1
    
    def _modify_environment_event(self, event_config: Dict, simulation):
        """Çevre değişikliği olayı"""
        modification_type = event_config.get('modification_type', 'food_spawn_rate')
        
        if modification_type == 'food_spawn_rate':
            new_rate = event_config.get('new_rate', 0.1)
            simulation.food_spawner.spawn_config['spawn_rate'] = new_rate
        
        elif modification_type == 'world_expansion':
            direction = event_config.get('direction', 'right')
            amount = event_config.get('amount', 500)
            simulation.world.expand_world(direction, amount)
    
    def _change_parameters_event(self, event_config: Dict, simulation):
        """Parametre değişikliği olayı"""
        parameters = event_config.get('parameters', {})
        
        for param_name, new_value in parameters.items():
            if hasattr(simulation, param_name):
                setattr(simulation, param_name, new_value)
            elif hasattr(simulation.config, param_name):
                simulation.config[param_name] = new_value
    
    def _custom_event(self, event_name: str, event_config: Dict, simulation):
        """Özel olay"""
        if self.scenario_instance and hasattr(self.scenario_instance, 'handle_event'):
            self.scenario_instance.handle_event(event_name, event_config, simulation)
            self.stats['custom_actions'] += 1
    
    def visualize(self, simulation):
        """Görselleştirme özelleştirmeleri"""
        if self.scenario_instance and hasattr(self.scenario_instance, 'visualize'):
            try:
                self.scenario_instance.visualize(simulation)
            except Exception as e:
                logger.error(f"Görselleştirme sırasında hata: {e}")
    
    def cleanup(self):
        """Senaryoyu temizle"""
        if self.scenario_instance and hasattr(self.scenario_instance, 'cleanup'):
            try:
                self.scenario_instance.cleanup()
                self.is_active = False
                logger.info(f"🎭 Senaryo temizlendi: {self.scenario_name}")
            except Exception as e:
                logger.error(f"Senaryo temizlenirken hata: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Senaryo hakkında bilgi döndür"""
        return {
            'name': self.scenario_name,
            'is_loaded': self.is_loaded,
            'is_active': self.is_active,
            'config': self.config,
            'stats': self.stats,
            'description': getattr(self.scenario_instance, 'description', 'Açıklama yok')
        }
    
    def get_available_scenarios(self) -> list:
        """Mevcut senaryoları listele"""
        scenarios_dir = Path("scenarios")
        if not scenarios_dir.exists():
            return []
        
        available_scenarios = []
        for scenario_dir in scenarios_dir.iterdir():
            if scenario_dir.is_dir() and (scenario_dir / "scenario.py").exists():
                available_scenarios.append(scenario_dir.name)
        
        return available_scenarios 