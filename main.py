#!/usr/bin/env python3
"""
Ecosim - Evrimsel Biyoloji Simülasyonu
Ana başlatıcı dosya
"""

import sys
import os
import argparse
import yaml
from pathlib import Path

# Core modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
from core.simulation import Simulation
from core.scenario_handler import ScenarioHandler

def load_config(config_path):
    """YAML config dosyasını yükle"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description='Ecosim - Evrimsel Biyoloji Simülasyonu')
    parser.add_argument('--scenario', '-s', default='default', 
                       help='Çalıştırılacak senaryo adı')
    parser.add_argument('--config', '-c', 
                       help='Özel config dosyası yolu')
    parser.add_argument('--headless', action='store_true',
                       help='Görsel olmadan sadece simülasyon çalıştır')
    parser.add_argument('--export', '-e', action='store_true',
                       help='Simülasyon sonuçlarını dışa aktar')
    
    args = parser.parse_args()
    
    # Senaryo yapılandırmasını yükle
    if args.config:
        config = load_config(args.config)
    else:
        scenario_path = Path(f"scenarios/{args.scenario}/config.yaml")
        if scenario_path.exists():
            config = load_config(scenario_path)
        else:
            print(f"Uyarı: {scenario_path} bulunamadı, varsayılan config kullanılıyor")
            config = {
                'simulation': {
                    'fps': 60,
                    'max_organisms': 1000,
                    'world_size': [2000, 2000]
                },
                'organism': {
                    'initial_count': 100,
                    'mutation_rate': 0.1,
                    'energy_decay': 0.1
                },
                'food': {
                    'spawn_rate': 0.05,
                    'energy_value': 10
                }
            }
    
    # Simülasyonu başlat
    try:
        simulation = Simulation(config, headless=args.headless)
        scenario_handler = ScenarioHandler(args.scenario, simulation)
        
        print(f"🎮 Ecosim başlatılıyor...")
        print(f"📊 Senaryo: {args.scenario}")
        print(f"⚙️  Config: {config.get('simulation', {})}")
        
        # Ana simülasyon döngüsü
        simulation.run(scenario_handler)
        
        if args.export:
            simulation.export_results()
            
    except KeyboardInterrupt:
        print("\n⏹️  Simülasyon kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 