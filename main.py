# main.py
"""
Doğal seleksiyon simülasyonunun ana döngüsü. Pygame ile görselleştirme ve günlük istatistikler.
Simülasyon sonunda matplotlib ile grafik çizilir.
"""
import sys
import time
import pygame
from settings import *
from simulation import (
    spawn_initial_blobs, spawn_food, handle_eating, next_generation,
    average_speed, average_sense, average_size
)
from graph import graph

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Doğal Seleksiyon Simülasyonu')
    clock = pygame.time.Clock()

    blobs = spawn_initial_blobs()
    day = 1

    while True:
        foods = spawn_food()
        day_start_time = time.time()
        # Gün döngüsü
        while time.time() - day_start_time < DAY_LENGTH:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # Canlılar hareket eder
            for blob in blobs:
                if blob.energy > 0:
                    blob.move(foods, blobs)
            # Yeme işlemi
            handle_eating(blobs, foods)
            # Çizim
            screen.fill(BG_COLOR)
            for food in foods:
                pygame.draw.circle(screen, FOOD_COLOR, (int(food.x), int(food.y)), FOOD_RADIUS)
            for blob in blobs:
                pygame.draw.circle(screen, blob.get_color(), (int(blob.x), int(blob.y)), blob.get_radius())
            pygame.display.flip()
            clock.tick(FPS)
        # Gün sonu: hayatta kalanlar ve üreme
        blobs = next_generation(blobs)
        # İstatistikler
        pop_size = len(blobs)
        avg_speed = average_speed(blobs)
        avg_sense = average_sense(blobs)
        avg_size = average_size(blobs)
        print(f"Gün {day}: Popülasyon = {pop_size}, Ortalama hız = {avg_speed:.2f}, Ortalama menzil = {avg_sense:.2f}, Ortalama boyut = {avg_size:.2f}")
        # Grafiğe veri ekle
        graph.update(day, avg_speed, avg_sense, avg_size)
        day += 1
        if pop_size == 0:
            print("Tüm canlılar öldü. Simülasyon sona erdi.")
            pygame.quit()
            break
    # Simülasyon bittiğinde grafik çiz
    graph.draw()

if __name__ == "__main__":
    main() 