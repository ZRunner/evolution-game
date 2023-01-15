from math import sqrt
from typing import TYPE_CHECKING

from pygame.math import Vector2

from . import config
from .utils import sign

if TYPE_CHECKING:
    from creature import Creature


class CreatureProcessMove:
    "Represents the data a process has to know in order to make a creature moving"
    def __init__(self, creature: "Creature"):
        self.creature_id = creature.creature_id
        self.size = creature.size
        self.own_acceleration = creature.own_acceleration
        self.acc = creature.acc
        self.vel = creature.vel
        self.deceleration = creature.deceleration
        self.pos = creature.pos
        self.energy = creature.energy
        self.light_emission = creature.light_emission
    
    def move(self, delta_t: int):
        "delta_t is time since last move in milliseconds"
        self._update_acceleration(delta_t)
        self._update_velocity(delta_t)
        new_pos = self.pos + 0.5 * (self.vel) * delta_t
        self._update_energy(new_pos, delta_t)
        self._update_position(new_pos)
    
    def _update_acceleration(self, delta_t: int):
        "Update the acceleration vector based on the given acceleration (from action neurons) and friction"
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
    
    def _update_velocity(self, delta_t: int):
        self.vel += self.acc / 100 * delta_t
        # calculate deceleration from config and current direction
        self.deceleration = Vector2(
            config.CREATURE_DECELERATION * sign(self.vel.x) * delta_t,
            config.CREATURE_DECELERATION * sign(self.vel.y) * delta_t
        )
        # make sure deceleration is not greater than current velocity
        if abs(self.deceleration.x) > abs(self.vel.x):
            self.deceleration.x = self.vel.x * 0.95
        if abs(self.deceleration.y) > abs(self.vel.y):
            self.deceleration.y = self.vel.y * 0.95
        # apply deceleration
        self.vel -= self.deceleration
        
        # apply max speed control
        if abs(self.vel.x) > config.MAX_CREATURE_VEL:
            self.vel.x = config.MAX_CREATURE_VEL * sign(self.vel.x)
        if abs(self.vel.y) > config.MAX_CREATURE_VEL:
            self.vel.y = config.MAX_CREATURE_VEL * sign(self.vel.y)
    
    def _update_energy(self, new_pos: Vector2, delta_t: int):
        distance = new_pos.distance_to(self.pos)
        if distance > 1e-5:
            self.energy -= distance * pow(self.size, 1.2) / (3.2 * delta_t)
        else: # if creature is immobile, make it hungry
            self.energy -= config.CREATURE_STILL_ENERGY * delta_t/1000
        
        # remove energy due to light emission
        light_points = self.light_emission * delta_t / 1000
        if light_points > 0:
            self.energy -= light_points / 700
    
    def _update_position(self, new_pos: Vector2):
        "Make sure the creature stays in the screen, then apply the given position"
        if new_pos.x > config.WIDTH:
            new_pos.x = 0
        elif new_pos.x < 0:
            new_pos.x = config.WIDTH
        if new_pos.y > config.HEIGHT:
            new_pos.y = 0
        elif new_pos.y < 0:
            new_pos.y = config.HEIGHT

        self.pos = new_pos
    
    def apply_to_creature(self, creature: "Creature"):
        creature.own_acceleration = self.own_acceleration
        creature.acc = self.acc
        creature.vel = self.vel
        creature.deceleration = self.deceleration
        creature.pos = self.pos
        creature.energy = self.energy
        creature.rectangle.center = (int(self.pos.x), int(self.pos.y))
        return creature

def mp_execute_move(arg: tuple[CreatureProcessMove, int]):
    creature, delta_t = arg
    creature.move(delta_t)
    return creature
