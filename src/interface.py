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
    fps_t = font.render(f"FPS: {fps}", True, Color(color))
    window.blit(fps_t,(3, 0))

def display_elapsed_time(window: Surface, font: Font, elapsed: float):
    "Display the elapsed time on top left corner"
    if minutes := elapsed // 60:
        seconds = elapsed % 60
        text = f"Time: {int(minutes)}m {seconds:.0f}s"
    else:
        text = f"Time: {elapsed:.1f}s"
    time_t = font.render(text, True, Color("WHITE"))
    window.blit(time_t, (3, 15))
