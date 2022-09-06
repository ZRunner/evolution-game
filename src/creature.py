from math import sqrt
import time
from random import gauss, randint, random, randrange
from typing import Optional, TYPE_CHECKING

from pygame import Color, Vector2, draw
from pygame.font import SysFont
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface

from src.gradients import draw_circle_gradient

from . import config
from .neural import NeuralNetwork
from .utils import sign

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

class Creature(Sprite):
    "A simple creature"

    def __init__(self, creature_id: int, generation: int):
        super().__init__()
        self.creature_id = creature_id
        self.generation = generation
        self.size = max(config.MIN_CREATURE_SIZE, round(gauss(
            config.CREATURE_SIZE_AVG, config.CREATURE_SIZE_SIGMA)))
        self.damager = DamageDisplayer(self.size)
        self.network = NeuralNetwork(
            randint(config.CREATURES_MIN_CONNECTIONS, config.CREATURES_MAX_CONNECTIONS),
            randrange(config.CREATURES_MAX_HIDDEN_NEURONS)
        )

        self.max_life = 10 + randrange(self.size * 10)
        self.life = self.max_life
        self.energy = config.CREATURE_STARTING_ENERGY
        self.life_regen_cost = round(self.size * randint(1, 5)) + 1
        self.digesting = config.CREATURE_MIN_STARTING_DIGESTING_POINTS + self.size
        self.digestion_efficiency = round(random() * 1.8 + 0.2, 2)
        self.digestion_speed = round(random() * 4 + 0.8, 1)
        self.vision = round(random() * 124 + 1)

        # neurons outputs
        self.own_acceleration = Vector2(0, 0)
        self.light_emission = 0.0
        self.ready_for_reproduction: bool = False

        self.color = self.calcul_color()
        self.font = SysFont("Arial", 12)
        self.surf = Surface((self.size, self.size))
        self.surf.fill(self.color)
        self.rectangle = self.surf.get_rect(
            center=(randrange(config.WIDTH), randrange(config.HEIGHT)))
        self.pos = Vector2(self.rectangle.center)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.deceleration = Vector2(0, 0)

    def calcul_color(self) -> Color:
        "Calcul the creature color based on its specs"
        life = min(255, 255 * self.max_life / 130)
        neurons_count = 255 * self.network.neurons_count / (config.CREATURES_MAX_CONNECTIONS + 5)
        third = 255
        return Color(f'#{int(life):02X}{int(neurons_count):02X}{third:02X}')

    def move(self, context: "ContextManager", delta_t: int):
        "delta_t is time since last move in milliseconds"
        self.network.update_input(self, context)
        self.network.tick()
        self.network.act(self)

        # calculate friction to apply to acceleration
        fr_max = Vector2(
            config.FRICTION * sqrt(self.size) * sign(self.own_acceleration.x),
            config.FRICTION * sqrt(self.size) * sign(self.own_acceleration.y)
        )
        if abs(fr_max.x) > abs(self.own_acceleration.x):
            fr_max.x = self.own_acceleration.x * 0.95
        if abs(fr_max.y) > abs(self.own_acceleration.y):
            fr_max.y = self.own_acceleration.y * 0.95

        self.acc = (self.own_acceleration - fr_max) / self.size

        # apply max acceleration control
        if abs(self.acc.x) > config.MAX_CREATURE_ACC:
            self.acc.x = config.MAX_CREATURE_ACC * sign(self.acc.x)
        if abs(self.acc.y) > config.MAX_CREATURE_ACC:
            self.acc.y = config.MAX_CREATURE_ACC * sign(self.acc.y)

        self.vel += self.acc / 100 * delta_t
        # apply deceleration
        self.deceleration = Vector2(
            config.CREATURE_DECELERATION * sign(self.vel.x),
            config.CREATURE_DECELERATION * sign(self.vel.y)
        )
        if abs(self.deceleration.x) > abs(self.vel.x):
            self.deceleration.x = self.vel.x * 0.95
        if abs(self.deceleration.y) > abs(self.vel.y):
            self.deceleration.y = self.vel.y * 0.95
        self.vel -= self.deceleration
        
        # apply max speed control
        if abs(self.vel.x) > config.MAX_CREATURE_VEL:
            self.vel.x = config.MAX_CREATURE_VEL * sign(self.vel.x)
        if abs(self.vel.y) > config.MAX_CREATURE_VEL:
            self.vel.y = config.MAX_CREATURE_VEL * sign(self.vel.y)

        new_pos = self.pos + 0.5 * (self.vel) * delta_t

        distance = new_pos.distance_to(self.pos)
        if distance > 1e-5:
            self.energy -= distance * pow(self.size, 1.2) / 60
        else: # if creature is immobile, make it hungry
            self.energy -= config.CREATURE_STILL_ENERGY * delta_t/1000
        
        # remove energy due to light emission
        light_points = self.light_emission * delta_t / 1000
        if light_points > 0:
            self.energy -= light_points / 700

        if new_pos.x > config.WIDTH:
            new_pos.x = 0
        elif new_pos.x < 0:
            new_pos.x = config.WIDTH
        if new_pos.y > config.HEIGHT:
            new_pos.y = 0
        elif new_pos.y < 0:
            new_pos.y = config.HEIGHT

        self.pos = new_pos
        self.rectangle.center = (int(self.pos.x), int(self.pos.y))

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
            draw_circle_gradient(surface, self.rectangle.center, self.light_emission, Color(255, 230, 100, min(255, self.light_emission)))

    def draw(self, surface: Surface, *, debug: bool=False, is_selected: bool=False):
        "Draw the sprite"
        surface.blit(self.surf, self.rectangle)
        if debug:
            acc_t = self.font.render(
                f"acc: ({self.acc.x*1000:.1f}, {self.acc.y*1000:.1f})", True, "white")
            surface.blit(acc_t, self.pos - Vector2(20, 32))
            vel_t = self.font.render(
                f"vel: ({self.vel.x*1000:.1f}, {self.vel.y*1000:.1f})", True, "white")
            surface.blit(vel_t, self.pos - Vector2(20, 22))
        if is_selected:
            self.draw_selection_frame(surface)
            self.draw_vision_circle(surface)
        if self.life < self.max_life:
            self.damager.draw(surface, self.rectangle)

    def eat(self, food: "FoodPoint"):
        "Eat a food point"
        self.digesting += food.quantity
