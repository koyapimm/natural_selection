"""
Ecosim Species Manager - Tür Yönetimi ve Biome Uyumluluğu
"""

import yaml
import random
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from .utils import logger

class SpeciesManager:
    """Tür yönetimi ve biome uyumluluğu için sınıf"""
    
    def __init__(self, config_path: str = "data/species_config.yaml"):
        self.config_path = config_path
        self.species_config = {}
        self.species_list = []
        self.load_species_config()
        
    def load_species_config(self):
        """Tür konfigürasyonunu yükle"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.species_config = yaml.safe_load(file)
                self.species_list = list(self.species_config.keys())
                logger.info(f"🌿 {len(self.species_list)} tür yüklendi: {', '.join(self.species_list)}")
        except Exception as e:
            logger.error(f"Tür konfigürasyonu yüklenirken hata: {e}")
            logger.error(f"Dosya yolu: {self.config_path}")
            # Varsayılan türler
            self.species_config = self._get_default_species()
            self.species_list = list(self.species_config.keys())
    
    def _get_default_species(self) -> Dict[str, Any]:
        """Varsayılan tür konfigürasyonu"""
        return {
            'rabbit': {
                'name': 'Tavşan',
                'biome_pref': ['grassland', 'forest'],
                'diet_type': 'herbivore',
                'speed': 35.0,
                'size': 2.5,
                'vision_range': 80.0,
                'metabolism': 0.12,
                'aggression': 0.1,
                'reproduction_threshold': 60.0,
                'energy_efficiency': 1.2,
                'social_attraction': 0.4,
                'exploration_tendency': 0.7,
                'lifespan': 80.0,
                'color_r': 0.9,
                'color_g': 0.8,
                'color_b': 0.7,
                'spawn_weight': 0.3
            },
            'deer': {
                'name': 'Geyik',
                'biome_pref': ['forest', 'grassland'],
                'diet_type': 'herbivore',
                'speed': 45.0,
                'size': 4.0,
                'vision_range': 150.0,
                'metabolism': 0.15,
                'aggression': 0.2,
                'reproduction_threshold': 75.0,
                'energy_efficiency': 1.0,
                'social_attraction': 0.6,
                'exploration_tendency': 0.5,
                'lifespan': 120.0,
                'color_r': 0.7,
                'color_g': 0.6,
                'color_b': 0.4,
                'spawn_weight': 0.2
            },
            'wolf': {
                'name': 'Kurt',
                'biome_pref': ['forest', 'grassland'],
                'diet_type': 'carnivore',
                'speed': 50.0,
                'size': 3.5,
                'vision_range': 180.0,
                'metabolism': 0.18,
                'aggression': 0.8,
                'reproduction_threshold': 85.0,
                'energy_efficiency': 0.9,
                'social_attraction': 0.7,
                'exploration_tendency': 0.8,
                'lifespan': 100.0,
                'color_r': 0.6,
                'color_g': 0.6,
                'color_b': 0.6,
                'spawn_weight': 0.1
            },
            'bear': {
                'name': 'Ayı',
                'biome_pref': ['forest', 'mountain'],
                'diet_type': 'omnivore',
                'speed': 30.0,
                'size': 5.0,
                'vision_range': 120.0,
                'metabolism': 0.10,
                'aggression': 0.4,
                'reproduction_threshold': 90.0,
                'energy_efficiency': 1.3,
                'social_attraction': 0.2,
                'exploration_tendency': 0.4,
                'lifespan': 150.0,
                'color_r': 0.5,
                'color_g': 0.4,
                'color_b': 0.3,
                'spawn_weight': 0.1
            }
        }
    
    def get_species_for_biome(self, biome_name: str) -> List[str]:
        """Belirli biome için uygun türleri döndür"""
        suitable_species = []
        
        for species_name, species_data in self.species_config.items():
            if biome_name in species_data.get('biome_pref', []):
                suitable_species.append(species_name)
        
        return suitable_species
    
    def select_random_species_for_biome(self, biome_name: str) -> Optional[str]:
        """Biome için rastgele tür seç (ağırlıklı seçim)"""
        suitable_species = self.get_species_for_biome(biome_name)
        
        if not suitable_species:
            return None
        
        # Ağırlıklı rastgele seçim
        weights = []
        for species in suitable_species:
            weight = self.species_config[species].get('spawn_weight', 0.1)
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            normalized_weights = [w / total_weight for w in weights]
            return random.choices(suitable_species, weights=normalized_weights)[0]
        
        return random.choice(suitable_species)
    
    def get_species_traits(self, species_name: str) -> Dict[str, Any]:
        """Tür özelliklerini döndür"""
        if species_name in self.species_config:
            return self.species_config[species_name].copy()
        return {}
    
    def get_species_name(self, species_name: str) -> str:
        """Türün görünen adını döndür"""
        if species_name in self.species_config:
            return self.species_config[species_name].get('name', species_name)
        return species_name
    
    def get_diet_type(self, species_name: str) -> str:
        """Türün beslenme tipini döndür"""
        if species_name in self.species_config:
            return self.species_config[species_name].get('diet_type', 'omnivore')
        return 'omnivore'
    
    def get_all_species_info(self) -> Dict[str, Dict[str, Any]]:
        """Tüm türlerin bilgilerini döndür"""
        return self.species_config.copy()
    
    def get_species_statistics(self) -> Dict[str, Any]:
        """Tür istatistiklerini döndür"""
        stats = {
            'total_species': len(self.species_list),
            'diet_types': {},
            'biome_distribution': {}
        }
        
        # Beslenme tipi dağılımı
        for species_name, species_data in self.species_config.items():
            diet_type = species_data.get('diet_type', 'omnivore')
            stats['diet_types'][diet_type] = stats['diet_types'].get(diet_type, 0) + 1
        
        # Biome dağılımı
        for species_name, species_data in self.species_config.items():
            for biome in species_data.get('biome_pref', []):
                stats['biome_distribution'][biome] = stats['biome_distribution'].get(biome, 0) + 1
        
        return stats 