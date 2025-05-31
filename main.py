# main.py
"""
Doğal seleksiyon simülasyonunun ana döngüsü. Pygame ile görselleştirme ve günlük istatistikler.
Her 10 günde bir tüm istatistik ve jenerasyon grafikleri ekrana gösterilir.
"""
import sys
import time
import pygame
import os
import json
import matplotlib.pyplot as plt
from settings import *
from simulation import (
    spawn_initial_blobs, spawn_food, handle_eating, next_generation,
    average_speed, average_sense, average_size, save_genealogy, apply_niche_bonus, increment_blob_ages
)
from graph import show_all_status
from utils import clamp, distance, diversity_score
from stats import StatsCollector

def get_generation_counts(blobs):
    """Her jenerasyonun hayatta kalan birey sayısını döndürür."""
    gen_counts = {}
    for blob in blobs:
        gen_key = f"jenerasyon_{blob.generation}"
        gen_counts[gen_key] = gen_counts.get(gen_key, 0) + 1
    return gen_counts

def main():
    # genealogy.json dosyasını her simülasyon başında sıfırla (overwrite)
    with open("genealogy.json", "w", encoding="utf-8") as f:
        json.dump({}, f)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Doğal Seleksiyon Simülasyonu')
    clock = pygame.time.Clock()

    blobs = spawn_initial_blobs()
    day = 1

    # StatsCollector başlat
    stats = StatsCollector()

    # İstatistik listeleri
    populations = []
    avg_speeds = []
    avg_senses = []
    avg_sizes = []
    energy_history = []
    diversity_scores = []

    # Görsel toggles
    show_vision = False
    show_energy_halo = False
    show_generation_label = False

    pop_size_start = len(blobs)
    avg_speed_start = average_speed(blobs)
    avg_sense_start = average_sense(blobs)
    avg_size_start = average_size(blobs)

    print(f"Gün 0: Popülasyon = {pop_size_start}, Ortalama hız = {avg_speed_start:.2f}, Ortalama menzil = {avg_sense_start:.2f}, Ortalama boyut = {avg_size_start:.2f}")
    save_genealogy(0, blobs)
    populations.append(pop_size_start)
    avg_speeds.append(avg_speed_start)
    avg_senses.append(avg_sense_start)
    avg_sizes.append(avg_size_start)

    font = pygame.font.SysFont(None, 16)

    # --- Niche bonusu ilk günde uygula ---
    apply_niche_bonus(blobs)

    while True:
        # İlk günlerde yemek sayısı artırılır
        if day <= EARLY_FOOD_DAYS:
            food_count = int(BASE_FOOD_COUNT * EARLY_FOOD_MULTIPLIER)
        else:
            food_count = BASE_FOOD_COUNT
        foods = spawn_food(food_count)
        # --- Niche bonusu ve yaş güncellemesi her gün başında ---
        apply_niche_bonus(blobs)
        increment_blob_ages(blobs)
        day_start_time = time.time()
        # Gün döngüsü
        while time.time() - day_start_time < DAY_LENGTH:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_v:
                        show_vision = not show_vision
                    if event.key == pygame.K_e:
                        show_energy_halo = not show_energy_halo
                    if event.key == pygame.K_g:
                        show_generation_label = not show_generation_label
            # Canlılar hareket eder
            for blob in blobs:
                if blob.alive:
                    blob.move(foods, blobs, day=day)
                blob.update()
            # Yeme işlemi
            handle_eating(blobs, foods)
            # Enerji ve yaşam kontrolü: yeme ve enerji güncellendikten sonra alive güncelle
            for blob in blobs:
                if blob.alive and blob.energy <= 0:
                    blob.alive = False
            # Çizim
            screen.fill(BG_COLOR)
            for food in foods:
                pygame.draw.circle(screen, FOOD_COLOR, (int(food.x), int(food.y)), FOOD_RADIUS)
            # Blobs: draw alive and dead (fading) blobs
            for blob in blobs:
                # Vision efekti: Her blob için yeni Surface oluşturma, doğrudan ana surface'e çiz
                if show_vision:
                    pygame.draw.circle(screen, (100, 200, 255, 40), (int(blob.x), int(blob.y)), int(blob.sense), 1)
                blob.draw(screen, False, show_energy_halo, show_generation_label, font)
            # Remove blobs that have fully faded out
            blobs = [b for b in blobs if not (not b.alive and b.fade_alpha == 0)]
            pygame.display.flip()
            clock.tick(FPS)
        # Gün sonu: hayatta kalanlar ve üreme
        blobs = next_generation(blobs, day)
        # İstatistikler
        pop_size = len(blobs)
        avg_speed = average_speed(blobs)
        avg_sense = average_sense(blobs)
        avg_size = average_size(blobs)
        diversity = diversity_score(blobs)
        diversity_scores.append(diversity)
        # Enerji histogramı için enerji değerlerini topla
        energy_history.append([b.energy for b in blobs])
        print(f"Gün {day}: Popülasyon = {pop_size}, Ortalama hız = {avg_speed:.2f}, Ortalama menzil = {avg_sense:.2f}, Ortalama boyut = {avg_size:.2f}, Çeşitlilik = {diversity:.3f}")
        save_genealogy(day, blobs)
        populations.append(pop_size)
        avg_speeds.append(avg_speed)
        avg_senses.append(avg_sense)
        avg_sizes.append(avg_size)
        # Adaptif mutasyon oranı güncellemesi
        global MUTATION_RATE
        if diversity < DIVERSITY_THRESHOLD:
            # Çeşitlilik düşükse, mutasyon oranını artır
            MUTATION_RATE = min(MAX_MUTATION_RATE, BASE_MUTATION_RATE * 2.5)
        else:
            MUTATION_RATE = BASE_MUTATION_RATE
        # StatsCollector ile veri topla
        stats.collect(day, blobs)
        # İstatistiksel analiz ve görselleştirme (tamamen main.py'den kontrol)
        if ENABLE_STATS and day % STATS_PLOT_INTERVAL == 0:
            stats.plot_trait_distributions(len(stats.days)-1)
            stats.plot_trait_stats_over_time()
            stats.plot_generation_stats()
            stats.plot_generation_depth()
            for trait in ['speed', 'size', 'sense']:
                stats.plot_survival_rate_heatmap(trait)
            stats.save_csv()
            stats.check_extinction_convergence(len(stats.days)-1)
        # Her 10 günde bir tüm istatistik ve jenerasyon grafiğini ekrana göster
        if day % 50 == 0:
            pygame.display.iconify()  # Pygame penceresini simge durumuna küçült
            show_all_status(day, populations, avg_speeds, avg_senses, avg_sizes, genealogy_json_path="genealogy.json", energy_list=energy_history)
            pygame.display.set_mode((WIDTH, HEIGHT))  # Pencereyi geri getir
        day += 1
        if pop_size == 0:
            print("Tüm canlılar öldü. Simülasyon sona erdi.")
            pygame.quit()
            break

if __name__ == "__main__":
    main() 