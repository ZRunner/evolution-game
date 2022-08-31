from math import ceil
from pygame import SRCALPHA
from pygame.color import Color
from pygame.math import Vector2
from pygame.surface import Surface
from pygame.draw import circle

def draw_circle_gradient(surface: Surface, center: Vector2, radius: int, color: Color):
    "Draw a gradient circle"
    subsurface = Surface((radius*2, radius*2), SRCALPHA)
    first_alpha = color.a
    alpha_step = first_alpha / radius
    circle_color = Color(color.r, color.g, color.b, 255)
    for i in range(0, radius, 1):
        circle_color.a = ceil(first_alpha - alpha_step * i)
        circle(subsurface, circle_color, Vector2(radius, radius), i, width=1)
    surface.blit(subsurface, center - Vector2(radius, radius))
