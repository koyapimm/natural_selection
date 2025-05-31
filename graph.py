"""
Her 10 günde bir jenerasyon bazlı popülasyon grafiğini ekrana gösteren fonksiyon.
"""
import matplotlib.pyplot as plt
import matplotlib.cm
import numpy as np
import json
import os

def show_generation_status(days, genealogy_json_path='genealogy.json'):
    """
    genealogy.json dosyasından jenerasyon bazlı popülasyon grafiğini ekrana gösterir.
    days: toplam gün sayısı veya gün listesi
    """
    if not os.path.exists(genealogy_json_path):
        print('genealogy.json bulunamadı.')
        return
    with open(genealogy_json_path, 'r', encoding='utf-8') as f:
        genealogy = json.load(f)
    generations = set()
    for day_data in genealogy.values():
        generations.update(day_data.keys())
    generations = sorted(generations, key=lambda x: int(x.split('_')[1]))
    gen_counts = {g: [] for g in generations}
    for day in [f"Gün {d}" for d in (days if isinstance(days, list) else range(days+1))]:
        day_data = genealogy.get(day, {})
        for g in generations:
            gen_counts[g].append(day_data.get(g, 0))
    plt.figure(figsize=(8, 5))
    for g in generations:
        plt.plot(range(len(gen_counts[g])), gen_counts[g], label=g)
    plt.xlabel('Gün')
    plt.ylabel('Popülasyon')
    plt.title('Jenerasyon Bazlı Popülasyon Durumu')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def show_all_status(days, populations, avg_speeds, avg_senses, avg_sizes, genealogy_json_path='genealogy.json', energy_list=None):
    """
    Tüm istatistikleri ve jenerasyon takibini tek bir figürde gösterir.
    days: int veya gün listesi
    populations, avg_speeds, avg_senses, avg_sizes: ilgili günlük değerler (list)
    genealogy_json_path: jenerasyon verisi dosyası
    energy_list: Her gün için ortalama enerji veya enerji dağılımı (opsiyonel)
    """
    fig, axs = plt.subplots(6, 1, figsize=(12, 18), sharex=True)
    # Popülasyon
    axs[0].plot(range(len(populations)), populations, color='black', label='Population')
    axs[0].set_ylabel('Pop.')
    axs[0].set_title('Evrimsel Simülasyon Sonuçları')
    axs[0].legend()
    axs[0].grid(True)
    # Ortalama hız
    axs[1].plot(range(len(avg_speeds)), avg_speeds, color='red', label='Speed')
    axs[1].set_ylabel('Hız')
    axs[1].legend()
    axs[1].grid(True)
    # Ortalama menzil
    axs[2].plot(range(len(avg_senses)), avg_senses, color='blue', label='Sense')
    axs[2].set_ylabel('Sense')
    axs[2].legend()
    axs[2].grid(True)
    # Ortalama boyut
    axs[3].plot(range(len(avg_sizes)), avg_sizes, color='green', label='Size')
    axs[3].set_ylabel('Size')
    axs[3].set_xlabel('Gün')
    axs[3].legend()
    axs[3].grid(True)
    # Jenerasyonlara göre canlı sayısı (genealogy.json) - area plot
    if os.path.exists(genealogy_json_path):
        with open(genealogy_json_path, 'r', encoding='utf-8') as f:
            genealogy = json.load(f)
        generations = set()
        for day_data in genealogy.values():
            generations.update(day_data.keys())
        generations = sorted(generations, key=lambda x: int(x.split('_')[1]))
        gen_counts = {g: [] for g in generations}
        for day in [f"Gün {d}" for d in (days if isinstance(days, list) else range(days+1))]:
            day_data = genealogy.get(day, {})
            for g in generations:
                gen_counts[g].append(day_data.get(g, 0))
        # Area plot (stacked)
        X = np.arange(len(next(iter(gen_counts.values()), [])))
        Y = np.row_stack([gen_counts[g] for g in generations])
        cmap = matplotlib.cm.get_cmap('viridis', len(generations))
        colors = [cmap(i) for i in range(len(generations))]
        axs[4].stackplot(X, Y, labels=generations, colors=colors, alpha=0.8)
        axs[4].set_ylabel('Gene.')
        axs[4].set_xlabel('Gün')
        # Legend sağa alınır
        axs[4].legend(loc='center left', bbox_to_anchor=(1.01, 0.5), ncol=1, fontsize=8, frameon=False)
        axs[4].grid(True)
    else:
        axs[4].set_visible(False)
    # Enerji histogramı (her 10 günde bir veya energy_list verilirse)
    if energy_list is not None and len(energy_list) > 0:
        # Son günün enerji listesini al, sadece pozitif ve sıfırdan büyük değerleri kullan
        last_energy = [e for e in energy_list[-1] if e > 0]
        if len(last_energy) > 0:
            axs[5].cla()
            axs[5].hist(last_energy, bins=15, color='orange', alpha=0.7, edgecolor='black')
            axs[5].set_ylabel('Enerji')
            axs[5].set_xlabel('Enerji Dağılımı (Son Gün)')
            axs[5].set_title('Enerji Histogramı')
            axs[5].grid(True)
        else:
            axs[5].set_visible(False)
    else:
        axs[5].set_visible(False)
    plt.tight_layout()
    plt.show() 