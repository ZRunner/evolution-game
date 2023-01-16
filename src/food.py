from math import ceil, cos, pi, sin
from random import randint, random, randrange
from typing import Optional

from pygame import Color, Vector2, draw
from pygame.sprite import Sprite
from pygame.surface import Surface

from . import config


class FoodGenerator:
    """A point generating food in its range
    Profusion is the probability to spawn a food each second, between 0.0 and 1.0"""

    def __init__(self, position: Optional[Vector2], radius: int, profusion: float):
        if position is None:
            self.position = Vector2(randrange(config.WIDTH), randrange(config.HEIGHT))
        else:
            self.position = position
        self.radius = radius
        self.profusion = profusion

    def generate_position(self):
        "Generate a position inside the active circle"
        r = self.radius * random()  # pylint: disable=invalid-name
        theta = random() * 2 * pi
        x_coo = round(self.position.x + r * cos(theta))
        y_coo = round(self.position.y + r * sin(theta))
        if 0 < x_coo < config.WIDTH and 0 < y_coo < config.HEIGHT:
            return Vector2(x_coo, y_coo)
        return self.generate_position()

    def tick(self):
        "Possibly generate a new food point somewhere"
        if random() > self.profusion:
            return None
        position = self.generate_position()
        return FoodPoint(position, randint(2, 35))

    def draw(self, surface: Surface):
        "Draw the sprite"
        draw.circle(surface, Color("#009933"), self.position, self.radius, 1)

class FoodPoint(Sprite):
    "A food point collectible by creatures"

    def __init__(self, position: Vector2, quantity: int):
        super().__init__()
        self.position = position
        self.quantity = quantity

        self.size = ceil(self.quantity / 10)

        self.surf = Surface((self.size, self.size))
        self.surf.fill("green")
        self.rectangle = self.surf.get_rect(center=(self.position))

    def draw(self, surface: Surface):
        "Draw the sprite"
        surface.blit(self.surf, self.rectangle)
