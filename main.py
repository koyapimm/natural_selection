"""
main.py
Yapay yaşam simülasyonunun Pygame tabanlı ana döngüsünü başlatır.
Modüler yapı için sadece başlangıç noktasıdır.
"""

import pygame
import sys
import settings
from simulation import Simulation
import input_handler
import overlay

# TODO: Simulation, Blob, Food gibi sınıflar ayrı dosyalarda tanımlanacak

def main():
    # Pygame başlat
    pygame.init()
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption("Yapay Yaşam Simülasyonu")
    clock = pygame.time.Clock()

    # TODO: Simulation sınıfı tanımlandığında buradan import edilecek
    # simulation = Simulation()
    simulation = Simulation()  # Yer tutucu, ileride Simulation nesnesi olacak
    font = pygame.font.SysFont("Arial", 16)

    running = True
    while running:
        # FPS'e sabitle
        clock.tick(settings.SIMULATION_SPEED)

        # input_handler ile eventleri işle
        running = input_handler.handle_input()

        # Gün döngüsü: arkaplan rengini ayarla
        if settings.DAY_NIGHT_CYCLE:
            cycle_pos = (simulation.frame_count % settings.FRAMES_PER_DAY) / settings.FRAMES_PER_DAY
            # 0-0.5 gündüz, 0.5-1 gece, yumuşak geçiş
            def lerp_color(c1, c2, t):
                return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
            if cycle_pos < 0.5:
                t = cycle_pos * 2
                bg_color = lerp_color(settings.DAY_COLOR, settings.NIGHT_COLOR, t)
            else:
                t = (cycle_pos - 0.5) * 2
                bg_color = lerp_color(settings.NIGHT_COLOR, settings.DAY_COLOR, t)
            screen.fill(bg_color)
        else:
            screen.fill(settings.COLOR_BACKGROUND)

        # Simulation update sadece pause değilse
        if simulation and not settings.PAUSE_SIMULATION:
            simulation.update()  # Simülasyon mantığı burada çalışacak
        if simulation:
            simulation.draw(screen)  # Simülasyonun görsel çıktısı burada çizilecek
        # TODO: Blob ve Food nesneleri simulation içinde yönetilecek

        # Gün/gece oranı ve ortalama aggression hesapla
        if settings.DAY_NIGHT_CYCLE:
            cycle_pos = (simulation.frame_count % settings.FRAMES_PER_DAY) / settings.FRAMES_PER_DAY
            if cycle_pos < 0.5:
                day_night_ratio = cycle_pos * 2
            else:
                day_night_ratio = 1.0 - (cycle_pos - 0.5) * 2
        else:
            day_night_ratio = 0.0
        if simulation and hasattr(simulation, 'blobs') and simulation.blobs:
            avg_aggr = sum(b.dna["aggression"] for b in simulation.blobs) / len(simulation.blobs)
        else:
            avg_aggr = 0.0

        overlay.draw_overlay(screen, font, simulation.frame_count, avg_aggr, day_night_ratio, simulation.blobs)

        # Ekranı güncelle
        pygame.display.flip()
        # FPS göstergesi (sağ üst köşe)
        fps = clock.get_fps()
        fps_font = pygame.font.SysFont("Arial", 14)
        fps_text = fps_font.render(f"FPS: {fps:.1f}", True, (255,255,0))
        screen.blit(fps_text, (settings.SCREEN_WIDTH - 80, 10))

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 