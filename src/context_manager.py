import math
from multiprocessing.pool import Pool
from typing import Optional, TypeVar

import pygame

from . import config
from .creature import Creature, creature_reproduction
from .food import FoodGenerator, FoodPoint
from .mp_utils import CreatureProcessMove, mp_execute_move
from .utils import get_toroidal_distance

T = TypeVar("T", Creature, FoodPoint)

class ContextManager:
    "Store the game context and main actions"

    def __init__(self):
        self.time = 0.0 # in seconds
        self.creatures: dict[int, Creature] = {
            i: Creature(i, 0, 0.0) for i in range(config.INITIAL_CREATURES_COUNT)
        }
        self.highest_creature_id = config.INITIAL_CREATURES_COUNT - 1
        self.food_generators: list[FoodGenerator] = [
            FoodGenerator(None, 160, 0.8),
            FoodGenerator(None, 80, 0.5),
            FoodGenerator(None, 40, 0.3),
        ]
        self.grid_cell_size = 50
        self.grid_size = (config.WIDTH // self.grid_cell_size, config.HEIGHT // self.grid_cell_size)
        self.foods_grid: dict[tuple[int, int], list[FoodPoint]] = {
            (x, y): [] for x in range(self.grid_size[0]) for y in range(self.grid_size[1])
        }
        self.creatures_grid: dict[tuple[int, int], list[Creature]] = {
            (x, y): [] for x in range(self.grid_size[0]) for y in range(self.grid_size[1])
        }

    def get_grid_cell(self, position: pygame.Vector2) -> tuple[int, int]:
        "Return the grid cell of a position"
        grid_x = int(position.x) // self.grid_cell_size % self.grid_size[0]
        grid_y = int(position.y) // self.grid_cell_size % self.grid_size[1]
        return grid_x, grid_y

    def draw_grid(self, screen: pygame.Surface):
        "Draw a grid on the screen"
        color = (100, 150, 180)
        for x in range(self.grid_cell_size, config.WIDTH, self.grid_cell_size):
            pygame.draw.line(screen, color, (x, 0), (x, config.HEIGHT))
        for y in range(self.grid_cell_size, config.HEIGHT, self.grid_cell_size):
            pygame.draw.line(screen, color, (0, y), (config.WIDTH, y))

    def update_creatures_grid(self):
        "update the creatures grid map based on each creature position"
        for creatures_list in self.creatures_grid.values():
            creatures_list.clear()
        for creature in self.creatures.values():
            grid_cell = self.get_grid_cell(creature.position)
            self.creatures_grid[grid_cell].append(creature)

    def find_visible_creatures(self, creature: Creature):
        "Find the closest entity from a list of entities"
        entities: set[Creature] = set()

        # Iterate over neighboring cells within the creature's vision range
        left_index = int((creature.position.x - creature.vision_distance) // self.grid_cell_size)
        right_index = int((creature.position.x + creature.vision_distance) // self.grid_cell_size)
        top_index = int((creature.position.y - creature.vision_distance) // self.grid_cell_size)
        bottom_index = int((creature.position.y + creature.vision_distance) // self.grid_cell_size)
        for cell_x in range(left_index, right_index + 1):
            for cell_y in range(top_index, bottom_index + 1):
                cell_x %= self.grid_size[0]
                cell_y %= self.grid_size[1]

                # Iterate over entities in the cell
                for entity in self.creatures_grid[cell_x, cell_y]:
                    if isinstance(entity, Creature) and entity.creature_id == creature.creature_id:
                        continue
                    # Check if the other entity is within the vision angle
                    # TODO: the angle check doesn't take into account the toroidal grid
                    #  and will not validate an entity at the other side of the map
                    to_other_entity = entity.position - creature.position
                    angle = creature.direction.angle_to(to_other_entity)
                    if abs(angle) <= creature.vision_angle / 2:
                        # Compute distance (toroidal)
                        dx = abs(entity.position.x - creature.position.x) % config.WIDTH
                        dy = abs(entity.position.y - creature.position.y) % config.HEIGHT
                        distance = math.sqrt(dx ** 2 + dy ** 2)
                        if distance <= creature.vision_distance:
                            # Update closest entity
                            entities.add(entity)

        return entities

    def find_closest_entity(self, creature: Creature, entities_grid: dict[tuple[int, int], list[T]]) -> tuple[Optional[T], float]:
        "Find the closest entity from a list of entities"
        min_distance = float('inf')
        closest_entity: Optional[T] = None

        # Iterate over neighboring cells within the creature's vision range
        left_index = int((creature.position.x - creature.vision_distance) // self.grid_cell_size)
        right_index = int((creature.position.x + creature.vision_distance) // self.grid_cell_size)
        top_index = int((creature.position.y - creature.vision_distance) // self.grid_cell_size)
        bottom_index = int((creature.position.y + creature.vision_distance) // self.grid_cell_size)
        for cell_x in range(left_index, right_index + 1):
            for cell_y in range(top_index, bottom_index + 1):
                cell_x %= self.grid_size[0]
                cell_y %= self.grid_size[1]

                # Iterate over entities in the cell
                for entity in entities_grid[cell_x, cell_y]:
                    if isinstance(entity, Creature) and entity.creature_id == creature.creature_id:
                        continue
                    # Check if the other entity is within the vision angle
                    # TODO: the angle check doesn't take into account the toroidal grid
                    #  and will not validate an entity at the other side of the map
                    to_other_entity = entity.position - creature.position
                    angle = creature.direction.angle_to(to_other_entity)
                    if abs(angle) <= creature.vision_angle / 2:
                        # Compute distance (toroidal)
                        distance = get_toroidal_distance(
                            creature.position, entity.position,
                            config.WIDTH, config.HEIGHT
                        )
                        if distance <= min(min_distance, creature.vision_distance):
                            # Update closest entity
                            min_distance = distance
                            closest_entity = entity

        return closest_entity, min_distance

    def update_creatures_energies(self):
        "Update creatures energies and life, and remove killed ones"
        to_die: set[int] = set()
        for entity in self.creatures.values():
            entity.update_energy()
            if entity.life <= 0:
                to_die.add(entity.creature_id)
        for entity_id in to_die:
            del self.creatures[entity_id]
        if to_die:
            print(len(to_die), "creature(s) died")

    def generate_initial_food(self):
        "Generate initial food points"
        for generator in self.food_generators:
            for _ in range(config.INITIAL_FOOD_QUANTITY):
                if food := generator.tick():
                    grid_cell = self.get_grid_cell(food.position)
                    self.foods_grid[grid_cell].append(food)

    def generate_food(self):
        "Generate food points around food generators"
        existing_food_count = sum(len(foods) for foods in self.foods_grid.values())
        max_to_generate = min(
            config.MAX_FOOD_GENERATED_PER_CYCLE,
            round(
                (config.MAX_FOOD_QUANTITY - existing_food_count)
                / len(self.food_generators) * 1.5
            )
        )
        for generator in self.food_generators:
            for _ in range(max_to_generate):
                if food := generator.tick():
                    grid_cell = self.get_grid_cell(food.position)
                    self.foods_grid[grid_cell].append(food)
                    existing_food_count += 1
                if existing_food_count >= config.MAX_FOOD_QUANTITY:
                    return

    def detect_creature_eating(self, creature: Creature):
        "Detect if a creature is eating a point, and make it happens"
        cell_x, cell_y = self.get_grid_cell(creature.position)
        # check the cell containing the creature AND the cells around it
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                cell = (cell_x + dx) % self.grid_size[0], (cell_y + dy) % self.grid_size[1]
                for food in self.foods_grid[cell]:
                    # if the creature reached its energy limit, stop the loop
                    if creature.energy > creature.max_energy:
                        creature.energy = creature.max_energy
                        return
                    if (
                        creature.rectangle.colliderect(food.rectangle)
                        and creature.max_digesting - creature.digesting > 0.5
                    ):
                        creature.eat(food)
                        self.foods_grid[cell].remove(food)

    def get_food_distance_for_creature(self, creature: Creature):
        "Get the distance between a creature and its nearest food point"
        best, distance = self.find_closest_entity(creature, self.foods_grid)
        return distance if best else None

    def get_light_level_for_creature(self, creature: Creature):
        "Get the current light level at the position of a creature"
        value = 0.0
        for neighbor in self.creatures.values():
            if (
                neighbor.creature_id != creature.creature_id
                and neighbor.light_emission > 0.0
            ):
                neighbor_distance = get_toroidal_distance(
                    creature.position, neighbor.position,
                    config.WIDTH, config.HEIGHT
                )
                if neighbor_distance < neighbor.light_emission:
                    value += neighbor.light_emission - neighbor_distance
        return value

    def reproduce_creatures(self):
        "If two creatures are in contact and ready to reproduce, make them have a child"
        children: set[Creature] = set()
        creatures = list(self.creatures.values())
        existing_creatures_count = len(self.creatures)
        for i, creature1 in enumerate(creatures):
            if len(children) > 20 or len(children) + existing_creatures_count >= config.MAX_CREATURES_COUNT:
                break
            for creature2 in creatures[i+1:]:
                if len(children) > 20 or len(children) + existing_creatures_count >= config.MAX_CREATURES_COUNT:
                    break
                if creature1.can_repro(self.time) and creature2.can_repro(self.time) and creature1.rectangle.colliderect(creature2.rectangle):
                    # create the child
                    child = creature_reproduction(creature1, creature2, self.highest_creature_id + 1, self.time)
                    # make it spawn between its parents
                    child.position.x = (creature1.position.x + creature2.position.x) / 2
                    child.position.y = (creature1.position.y + creature2.position.y) / 2
                    # add it to the list of newly born children
                    children.add(child)
                    # increment ID
                    self.highest_creature_id += 1
                    # update their parent
                    creature1.last_reproduction = self.time
                    creature2.last_reproduction = self.time
                    lost_energy = config.CREATURE_REPRO_ENERGY_FACTOR * (child.size ** 0.7)
                    creature1.energy -= lost_energy
                    creature2.energy -= lost_energy
                    # give 0.3x the energy of each parent to the child
                    child.energy = lost_energy * config.CHILD_INITIAL_ENERGY_PERCENT
                    # set the initial life of the child to 70% of parents avg. life
                    parents_life = (
                        creature1.life / creature1.max_life
                        + creature2.life / creature2.max_life
                    ) / 2
                    assert 0 <= parents_life <= 1
                    child.life = min(
                        round(child.max_life * parents_life * config.CHILD_INITIAL_LIFE_PERCENT),
                        child.max_life
                    )
        # add every new child into the Great List of Creatures
        children_list = list(children)[:10]
        for child in children_list:
            self.creatures[child.creature_id] = child
        if children_list:
            print(len(children_list), "new creature(s) born")

    def attack_creatures(self):
        "If one creature is ready to attack, make it attack the nearest creature"
        creatures = list(self.creatures.values())
        to_die: set[int] = set()
        for creature in creatures:
            if creature.max_damage > 0 and creature.can_attack(self.time):
                victim, _ = self.find_closest_entity(creature, self.creatures_grid)
                if victim is not None and victim.creature_id not in to_die:
                    distance = get_toroidal_distance(
                        creature.position, victim.position,
                        config.WIDTH, config.HEIGHT
                    )
                    relative_distance = 1 - distance / creature.vision_distance
                    damages = round(creature.max_damage * relative_distance)
                    assert damages >= 0
                    if damages != 0:
                        victim.receive_damages(damages)
                        creature.last_damage_action = self.time
                        victim.last_damage_received = self.time
                        if victim.life <= 0:
                            to_die.add(victim.creature_id)
        for entity_id in to_die:
            del self.creatures[entity_id]
        if to_die:
            print(len(to_die), "creature(s) died")

    def move_creatures(self, pool: Pool, delta_t: int):
        "Update creature networks and move them in batch using multiprocessing"
        arguments: list[tuple[CreatureProcessMove, int]] = []
        for creature in self.creatures.values():
            creature.update_network(self)
            arguments.append((CreatureProcessMove(creature), delta_t))
        for i in pool.imap_unordered(mp_execute_move, arguments, chunksize=40):
            i.apply_to_creature(self.creatures[i.creature_id])
