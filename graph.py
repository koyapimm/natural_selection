"""
Simülasyon verilerini toplayan ve simülasyon sonunda 3 ayrı çizgi grafiği tek figürde çizen modül.
"""
import matplotlib.pyplot as plt

class GraphManager:
    def __init__(self):
        self.days = []
        self.avg_speeds = []
        self.avg_senses = []
        self.avg_sizes = []

    def update(self, day, avg_speed, avg_sense, avg_size):
        self.days.append(day)
        self.avg_speeds.append(avg_speed)
        self.avg_senses.append(avg_sense)
        self.avg_sizes.append(avg_size)

    def draw(self):
        fig, axs = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
        # Ortalama hız
        axs[0].plot(self.days, self.avg_speeds, color='red')
        axs[0].set_ylabel('Ortalama Hız')
        axs[0].set_title('Evrimsel Simülasyon Sonuçları')
        axs[0].grid(True)
        # Ortalama menzil
        axs[1].plot(self.days, self.avg_senses, color='blue')
        axs[1].set_ylabel('Ortalama Menzil (Sense)')
        axs[1].grid(True)
        # Ortalama boyut
        axs[2].plot(self.days, self.avg_sizes, color='green')
        axs[2].set_ylabel('Ortalama Boyut (Size)')
        axs[2].set_xlabel('Gün')
        axs[2].grid(True)
        plt.tight_layout()
        plt.show()

# Tekil nesne
graph = GraphManager() 