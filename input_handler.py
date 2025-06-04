import pygame
import settings

def handle_input():
    """
    Klavye ile görsel modları dinamik olarak değiştirir.
    K_v: SHOW_VISION toggle
    K_e: SHOW_ENERGY_CIRCLE toggle
    K_m: SHOW_METABOLISM_COLOR toggle
    SPACE: Pause/Resume
    +: FPS artır
    -: FPS azalt
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False  # Ana döngüyü durdurmak için
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_v:
                settings.SHOW_VISION = not settings.SHOW_VISION
            elif event.key == pygame.K_e:
                settings.SHOW_ENERGY_CIRCLE = not settings.SHOW_ENERGY_CIRCLE
            elif event.key == pygame.K_m:
                settings.SHOW_METABOLISM_COLOR = not settings.SHOW_METABOLISM_COLOR
            elif event.key == pygame.K_SPACE:
                settings.PAUSE_SIMULATION = not settings.PAUSE_SIMULATION
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                settings.SIMULATION_SPEED = min(settings.SIMULATION_SPEED + 10, settings.SIMULATION_SPEED_MAX)
            elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                settings.SIMULATION_SPEED = max(settings.SIMULATION_SPEED - 10, settings.SIMULATION_SPEED_MIN)
    return True 