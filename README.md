# 🌱 Ecosim - Artificial Life Evolution Simulation

A GPU-accelerated, modular artificial life simulation engine based on evolutionary biology principles. Watch organisms evolve, compete, and adapt in an infinitely expandable 2D world.

## 🎯 Features

- **Evolutionary Biology**: Natural selection, mutation, speciation, and sexual selection
- **GPU Acceleration**: CuPy and Numba for high-performance computing
- **Modular Architecture**: Scenario-based system for flexible experimentation
- **Infinite World**: Scrollable 2D coordinate plane with free camera movement
- **Visual Analytics**: Real-time statistics and data export for content creation
- **Performance Optimized**: Level of Detail (LOD), frustum culling, and throttling

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (for GPU acceleration)
- Windows/Linux/macOS

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ecosim.git
   cd ecosim
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the simulation**
   ```bash
   python main.py --scenario default
   ```

## 🎮 Controls

- **WASD**: Camera movement
- **Mouse Wheel**: Zoom in/out
- **Mouse Drag**: Pan camera
- **F**: Toggle fullscreen
- **H**: Toggle HUD
- **ESC**: Exit

## 🧬 Simulation Components

### Core Modules
- **World**: Infinite 2D coordinate system with spatial hashing
- **Organism**: Genetic traits, behaviors, and evolution
- **Food**: Energy sources with different types and properties
- **Camera**: Free movement and zoom controls
- **Simulation**: Main loop and statistics management

### Organism Traits
- Speed, Vision Range, Aggression
- Size, Color, Lifespan
- Metabolism, Social Attraction
- Exploration Tendency

### Behaviors
- Wandering, Hunting, Fleeing
- Reproduction, Resting, Socializing
- Chasing Prey, Territory Defense

## 📊 Data & Analytics

The simulation exports comprehensive data for analysis:
- Population history and trends
- Genetic trait evolution
- Fitness statistics
- Food consumption patterns
- Performance metrics

## 🎨 Visual Features

- **Genetic-based Coloring**: Organisms colored by their traits
- **State Indicators**: Visual cues for energy, aggression, reproduction
- **Aura Effects**: Dynamic visual feedback for organism states
- **Level of Detail**: Adaptive rendering based on zoom level
- **Performance Monitoring**: Real-time FPS and component timings

## 🧪 Scenario System

Create custom scenarios to experiment with different evolutionary conditions:

```yaml
# scenarios/custom/config.yaml
simulation:
  max_organisms: 1000
  performance_mode: "balanced"

organism:
  initial_count: 50
  energy_decay: 0.12
  reproduction_threshold: 50.0

food:
  spawn_rate: 0.25
  energy_value: 15
```

## 📁 Project Structure

```
ecosim/
├── core/                 # Core simulation engine
│   ├── world.py         # World management
│   ├── organism.py      # Organism logic
│   ├── food.py          # Food system
│   ├── simulation.py    # Main simulation loop
│   ├── camera.py        # Camera controls
│   └── utils.py         # Utilities
├── visuals/             # Rendering system
│   ├── organism_renderer.py
│   ├── food_renderer.py
│   ├── ui_renderer.py
│   └── performance_monitor.py
├── scenarios/           # Scenario configurations
│   └── default/
├── data/               # Logs and exports
│   ├── logs/
│   ├── stats/
│   └── exports/
├── main.py             # Entry point
└── requirements.txt    # Dependencies
```

## 🔧 Configuration

The simulation is highly configurable through YAML files:

- **Simulation Parameters**: Population limits, performance settings
- **Organism Traits**: Genetic ranges, behavior probabilities
- **Food Properties**: Spawn rates, energy values, decay
- **Visual Settings**: Rendering quality, UI elements
- **Performance Modes**: Quality vs. speed optimization

## 📈 Content Creation

Perfect for creating educational content:
- **Social Media**: Short videos showing evolution in action
- **Educational**: Demonstrating biological concepts
- **Research**: Analyzing evolutionary patterns
- **Entertainment**: Engaging visual simulations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by Conway's Game of Life and modern evolutionary simulations
- Built with Pygame, NumPy, CuPy, and Numba
- Designed for educational and research purposes

## 📞 Support

For questions, issues, or contributions, please open an issue on GitHub.

---

**Happy evolving! 🌿** 