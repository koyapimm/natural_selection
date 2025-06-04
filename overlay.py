import pygame
import settings

def draw_overlay(screen, font, frame_count, avg_aggr=0.0, day_night_ratio=0.0, blobs=None):
    """
    Sol üst köşede klavye toggle durumlarını, frame bilgisini, ortalama aggression ve gün/gece oranını gösterir.
    FPS, pause durumu ve genetik/istatistiksel bilgiler de gösterilir.
    """
    # Genetik ortalamalar ve dağılımlar
    avg_speed = avg_size = avg_vision = 0.0
    meta_counts = {"day": 0, "night": 0, "neutral": 0}
    food_counts = {"green": 0, "red": 0, "blue": 0}
    pop = len(blobs) if blobs else 0
    if blobs and pop > 0:
        avg_speed = sum(b.dna["speed"] for b in blobs) / pop
        avg_size = sum(b.dna["size"] for b in blobs) / pop
        avg_vision = sum(b.dna["vision"] for b in blobs) / pop
        for b in blobs:
            meta = b.dna["metabolism"]
            if meta in meta_counts:
                meta_counts[meta] += 1
            pf = b.dna["preferred_food"]
            if pf in food_counts:
                food_counts[pf] += 1
    # Panel metinleri
    lines = [
        f"[V] Vision: {'ON' if settings.SHOW_VISION else 'OFF'}",
        f"[E] Energy Ring: {'ON' if settings.SHOW_ENERGY_CIRCLE else 'OFF'}",
        f"[M] Metabolism Color: {'ON' if settings.SHOW_METABOLISM_COLOR else 'OFF'}",
        f"[A] Aggression Aura: {'ON' if settings.SHOW_AGGRESSION_AURA else 'OFF'}",
        f"[H] Hunt Lines: {'ON' if settings.SHOW_HUNT_LINES else 'OFF'}",
        f"Day-Night Cycle: {'ON' if settings.DAY_NIGHT_CYCLE else 'OFF'}",
        f"Frame: {frame_count}",
        f"Avg Aggression: {avg_aggr:.3f}",
        f"Day/Night: {day_night_ratio:.2f}",
        f"FPS: {settings.SIMULATION_SPEED}",
        f"Pause: {'ON' if settings.PAUSE_SIMULATION else 'OFF'}",
        f"--- Genetics/Stats ---",
        f"Avg Speed: {avg_speed:.2f}",
        f"Avg Size: {avg_size:.1f}",
        f"Avg Vision: {avg_vision:.1f}",
        f"Metabolism: Day {meta_counts['day']}  Night {meta_counts['night']}  Neutral {meta_counts['neutral']}",
        f"Pref. Food: Green {food_counts['green']}  Red {food_counts['red']}  Blue {food_counts['blue']}"
    ]
    # Panel boyutları
    width = 260
    height = 24 * len(lines) + 10
    overlay_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay_surf.fill((30, 30, 30, 150))
    for i, text in enumerate(lines):
        text_surf = font.render(text, True, (255, 255, 255))
        overlay_surf.blit(text_surf, (10, 5 + i * 24))
    screen.blit(overlay_surf, (10, 10)) 