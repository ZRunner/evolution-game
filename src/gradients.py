from pygame import transform
from pygame.image import load as image_load
from pygame.math import Vector2
from pygame.surface import Surface

circle_img = image_load('src/lens_circle.png')
circle_scales_cache: dict[int, Surface] = {}

def _get_image_from_scale(radius: int):
    if radius not in circle_scales_cache:
        circle_scales_cache[radius] = transform.scale(circle_img, (radius*2, radius*2))
    return circle_scales_cache[radius]

def draw_circle_gradient(surface: Surface, center: Vector2, radius: int):
    "Draw a gradient circle, where the center is at full opacity and the edges are transparent"
    scaled_circle = _get_image_from_scale(radius)
    surface.blit(scaled_circle, center - Vector2(radius, radius))
