import time
from random import gauss, randint, random, randrange, uniform
from typing import TYPE_CHECKING, Optional, TypedDict

from pygame import Color, draw
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface

from src.gradients import draw_circle_gradient

from . import config
from .neural import NeuralNetwork

if TYPE_CHECKING:
    from context_manager import ContextManager
    from food import FoodPoint


class DamageDisplayer:
    "Display a fading red square over damaged creatures"
    def __init__(self, size: int, duration: float = 1.5):
        self.size = size
        self.last_hurt: Optional[float] = None
        self.duration = duration
        self.surface = Surface((self.size, self.size))

    def hurt(self):
        "Trigger the hurting animation"
        self.last_hurt = time.time()

    def draw(self, surface: Surface, rectangle: Rect):
        "Draw the square if needed"
        if self.last_hurt is None:
            return
        now = time.time()
        if now - self.last_hurt > self.duration:
            self.last_hurt = None
            return
        opacity = 1 - (now - self.last_hurt) / self.duration
        self.surface.set_alpha(round(opacity*255))
        self.surface.fill(Color(255, 0, 0))
        surface.blit(self.surface, rectangle)


def creature_reproduction(parent1: "Creature", parent2: "Creature", creature_id: int, timestamp: float) -> "Creature":
    "Use some random algorithms to merge two creatures into a new 'child'"
    size = randint(min(parent1.size, parent2.size), max(parent1.size, parent2.size))
    max_life = randint(min(parent1.max_life, parent2.max_life), max(parent1.max_life, parent2.max_life))
    life_regen_cost = randint(min(parent1.life_regen_cost, parent2.life_regen_cost), max(parent1.life_regen_cost, parent2.life_regen_cost))
    digestion_efficiency = uniform(min(parent1.digestion_efficiency, parent2.digestion_efficiency), max(parent1.digestion_efficiency, parent2.digestion_efficiency))
    digestion_speed = uniform(min(parent1.digestion_speed, parent2.digestion_speed), max(parent1.digestion_speed, parent2.digestion_speed))
    vision = randint(min(parent1.vision, parent2.vision), max(parent1.vision, parent2.vision))
    generation = max(parent1.generation, parent2.generation) + 1
    return Creature(
        creature_id,
        generation,
        timestamp,
        {
            "size": size,
            "network": NeuralNetwork.from_parents(parent1.network, parent2.network),
            "max_life": max_life,
            "life_regen_cost": life_regen_cost,
            "digestion_efficiency": digestion_efficiency,
            "digestion_speed": digestion_speed,
            "vision": vision,
        }
    )


class CreatureGeneratedAttributes(TypedDict):
    size: int
    network: NeuralNetwork
    max_life: int
    life_regen_cost: int
    digestion_efficiency: float
    digestion_speed: float
    vision: int

class Creature(Sprite):
    "A simple creature"

    def __init__(self, creature_id: int, generation: int, timestamp: float, kwargs: Optional[CreatureGeneratedAttributes] = None):
        super().__init__()
        self.creature_id = creature_id
        self.generation = generation

        # generated values
        if kwargs:
            self.size = kwargs.get("size")
            self.network = kwargs.get("network")
            self.max_life = kwargs.get("max_life")
            self.life_regen_cost = kwargs.get("life_regen_cost")
            self.digestion_efficiency = round(kwargs.get("digestion_efficiency"), 2)
            self.digestion_speed = round(kwargs.get("digestion_speed"), 1)
            self.vision = kwargs.get("vision")
        else:
            self.size = max(config.MIN_CREATURE_SIZE, round(gauss(
                config.CREATURE_SIZE_AVG, config.CREATURE_SIZE_SIGMA)))
            self.network = NeuralNetwork(
                randint(config.CREATURES_MIN_CONNECTIONS, config.CREATURES_MAX_CONNECTIONS),
                randrange(config.CREATURES_MAX_HIDDEN_NEURONS)
            )
            self.max_life = 8 + randrange(self.size * 10)
            self.life_regen_cost = round(self.size * randint(1, 5)) + 1
            self.digestion_efficiency = round(random() * 1.8 + 0.2, 2)
            self.digestion_speed = round(random() * 4 + 0.8, 1)
            self.vision = round(random() * 124 + 1)

        # neurons outputs
        self.own_acceleration = Vector2(0, 0)
        self.light_emission = 0.0
        self.ready_for_reproduction: bool = False

        # fixed attributes
        self.life = self.max_life
        self.energy: float = config.CREATURE_STARTING_ENERGY
        self.digesting = config.CREATURE_MIN_STARTING_DIGESTING_POINTS + self.size
        self.color = self.calcul_color()
        self.surf = Surface((self.size, self.size))
        self.surf.fill(self.color)
        self.rectangle = self.surf.get_rect(
            center=(randrange(config.WIDTH), randrange(config.HEIGHT)))
        self.damager = DamageDisplayer(self.size)
        self.last_reproduction = timestamp
        self.birth = timestamp
        # some vectors
        self.pos = Vector2(self.rectangle.center)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.deceleration = Vector2(0, 0)

    def can_repro(self, timestamp: float):
        return self.ready_for_reproduction and timestamp - self.last_reproduction > config.CREATURE_REPRO_COOLDOWN

    def calcul_color(self) -> Color:
        "Calcul the creature color based on its specs"
        life = min(255, 255 * self.max_life / 130)
        neurons_count = min(255, 255 * self.network.neurons_count / (config.CREATURES_MAX_CONNECTIONS + 5))
        third = 255
        return Color(f'#{int(life):02X}{int(neurons_count):02X}{third:02X}')
    
    def update_network(self, context: "ContextManager"):
        self.network.update_input(self, context)
        self.network.tick()
        self.network.act(self)


    def update_energy(self):
        "Update the creature energy, life and digestion"
        # dugestion
        points = min(self.digesting, self.digestion_speed)
        if points > 0:
            self.digesting -= points
            self.digesting = round(self.digesting, 5)
            self.energy += points * self.digestion_efficiency
        # life damages
        if self.energy <= -10:
            self.life += round(self.energy / 10)
            self.damager.hurt()
            self.energy = 0
        # life regeneration
        elif self.energy >= self.life_regen_cost and self.life < self.max_life:
            self.energy -= self.life_regen_cost
            self.life += 1

    def draw_selection_frame(self, surface: Surface):
        "Draw a red frame around the creature when it has been selected by the user"
        size = self.surf.get_size()[0]/2 + 5
        centerx, centery = self.rectangle.center
        # top left line
        space = 3
        draw.line(surface, "red",
                    (centerx - size,  centery - size), # top left
                    (centerx - space, centery - size)  # top center left
                    )
        # left top line
        draw.line(surface, "red",
                    (centerx - size,  centery - size), # top left
                    (centerx - size,  centery - space) # left center top
                    )
        # top right line
        draw.line(surface, "red",
                    (centerx + size,  centery - size),  # top right
                    (centerx + space, centery - size)   # top center right
                    )
        # right top line
        draw.line(surface, "red",
                    (centerx + size,  centery - size),  # top right
                    (centerx + size,  centery - space)  # right center top
                    )
        # bottom left line
        draw.line(surface, "red",
                    (centerx - size,  centery + size), # bottom left
                    (centerx - space, centery + size)  # bottom center left
                    )
        # left bottom line
        draw.line(surface, "red",
                    (centerx - size,  centery + size),  # bottom left
                    (centerx - size,  centery + space)  # bottom center left
                    )
        # bottom right line
        draw.line(surface, "red",
                    (centerx + size,  centery + size),  # bottom right
                    (centerx + space, centery + size)   # bottom center right
                    )
        # right bottom line
        draw.line(surface, "red",
                    (centerx + size,  centery + size),  # bottom right
                    (centerx + size,  centery + space)  # right center bottom
                    )
    
    def draw_vision_circle(self, surface: Surface):
        "Draw a circle representing the entity vision"
        draw.circle(surface, "aqua", self.rectangle.center, self.vision, width=1)
    
    def draw_light_circle(self, surface: Surface):
        "Draw a circle representing the emitted light"
        if self.light_emission > 0:
            # print(self.creature_id, self.light_emission)
            draw_circle_gradient(
                surface,
                Vector2(self.rectangle.center),
                round(self.light_emission),
                Color(255, 230, 100, min(255, int(self.light_emission)))
                )

    def draw(self, surface: Surface, is_selected: bool=False):
        "Draw the sprite"
        surface.blit(self.surf, self.rectangle)
        if is_selected:
            self.draw_selection_frame(surface)
            self.draw_vision_circle(surface)
        if self.life < self.max_life:
            self.damager.draw(surface, self.rectangle)

    def eat(self, food: "FoodPoint"):
        "Eat a food point"
        self.digesting += food.quantity
