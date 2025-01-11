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
        self.acceleration_from_neuron = creature.acceleration_from_neuron
        self.rotation_from_neuron = creature.rotation_from_neuron
        self.direction = creature.direction
        self.acceleration = creature.acceleration
        self.velocity = creature.velocity
        self.deceleration = creature.deceleration
        self.pos = creature.position
        self.energy = creature.energy
        self.light_emission = creature.light_emission

    def move(self, delta_t: int):
        "delta_t is time since last move in milliseconds"
        self._update_acceleration(delta_t)
        self._update_velocity(delta_t)
        self._update_direction(delta_t)
        new_pos = self.pos + 0.5 * self.direction * self.velocity * delta_t
        self._update_energy(new_pos, delta_t)
        self._update_position(new_pos)

    def _update_acceleration(self, _delta_t: int):
        "Update the acc. vector based on the given acceleration (from action neurons) and friction"
        # calculate friction to apply to acceleration
        fr_max = config.FRICTION * sqrt(self.size) * sign(self.acceleration_from_neuron)
        if abs(fr_max) > abs(self.acceleration_from_neuron):
            fr_max = self.acceleration_from_neuron * 0.95

        self.acceleration = (self.acceleration_from_neuron - fr_max) / self.size

        # apply max acceleration control
        if abs(self.acceleration) > config.MAX_CREATURE_ACC:
            self.acceleration = config.MAX_CREATURE_ACC * sign(self.acceleration)

    def _update_velocity(self, delta_t: int):
        self.velocity += self.acceleration / 100 * delta_t
        # calculate deceleration from config and current direction
        self.deceleration = config.CREATURE_DECELERATION * sign(self.velocity) * delta_t
        # make sure deceleration is not greater than current velocity
        if abs(self.deceleration) > abs(self.velocity):
            self.deceleration = self.velocity * 0.95
        # apply deceleration
        self.velocity -= self.deceleration

        # apply max speed control
        if abs(self.velocity) > config.MAX_CREATURE_VEL:
            self.velocity = config.MAX_CREATURE_VEL * sign(self.velocity)

    def _update_direction(self, delta_t: int):
        self.direction = self.direction.rotate(self.rotation_from_neuron * delta_t)

    def _update_energy(self, new_pos: Vector2, delta_t: int):
        distance = new_pos.distance_to(self.pos)
        # base energy consumption from existing
        self.energy -= config.CREATURE_STILL_ENERGY * pow(self.size, 0.7) * delta_t/1000
        if distance > 1e-5:
            # energy consumption from movement
            self.energy -= pow(distance, 1.3) * pow(self.size, 1.1) / (4 * delta_t)

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
        "Apply the calculated changes to the given creature"
        creature.acceleration_from_neuron = self.acceleration_from_neuron
        creature.rotation_from_neuron = self.rotation_from_neuron
        creature.acceleration = self.acceleration
        creature.velocity = self.velocity
        creature.deceleration = self.deceleration
        creature.position = self.pos
        creature.direction = self.direction
        creature.energy = self.energy
        creature.rectangle.center = (int(self.pos.x), int(self.pos.y))
        return creature

def mp_execute_move(arg: tuple[CreatureProcessMove, int]):
    "Update creature acceleration, velocity, direction, energy and position"
    creature, delta_t = arg
    creature.move(delta_t)
    return creature
