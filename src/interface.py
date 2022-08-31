from pygame import Color
from pygame.surface import Surface
from pygame.time import Clock
from pygame.font import Font

def display_fps(window: Surface, font: Font, clock: Clock):
    "Display current fps on top left corner"
    fps = int(clock.get_fps())
    if fps < 10:
        color = "RED"
    elif fps < 30:
        color = "YELLOW"
    else:
        color = "WHITE"
    fps_t = font.render(str(fps), True, Color(color))
    window.blit(fps_t,(0,0))
