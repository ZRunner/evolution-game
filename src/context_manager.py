import time
from multiprocessing.pool import Pool
from typing import Optional

from . import config
from .creature import Creature, creature_reproduction
from .food import FoodGenerator, FoodPoint
from .mp_utils import CreatureProcessMove, mp_execute_move


class ContextManager:

    def __init__(self):
        self.creatures: dict[int, Creature] = {i: Creature(i, 0, 0.0) for i in range(config.CREATURES_COUNT)}
        self.highest_creature_id = config.CREATURES_COUNT - 1
        self.food_generators: list[FoodGenerator] = [
            FoodGenerator(None, 160, 0.7),
            FoodGenerator(None, 80, 0.4),
            FoodGenerator(None, 40, 0.3),
        ]
        self.foods: list[FoodPoint] = []
        self.time = 0.0
    
    def update_creatures_energies(self):
        "Update creatures energies and life, and remove killed ones"
        to_die: list[int] = []
        for entity in self.creatures.values():
            entity.update_energy()
            if entity.life <= 0:
                to_die.append(entity.creature_id)
        for entity_id in to_die:
            del self.creatures[entity_id]
    
    def generate_food(self):
        "Generate food points around food generators"
        for generator in self.food_generators:
            if food := generator.tick():
                self.foods.append(food)

    def detect_creature_eating(self, creature: Creature):
        "Detect if a creature is eating a point, and make it happens"
        for food in self.foods:
            if creature.rectangle.colliderect(food.rectangle):
                creature.eat(food)
                self.foods.remove(food)
                break

    def get_food_distance_for_creature(self, creature: Creature):
        "Get the distance between a creature and its nearest food point"
        best: Optional[float] = None
        for food in self.foods:
            if best is None or food.position.distance_to(creature.pos) < best:
                best = food.position.distance_to(creature.pos)
        return best

    def get_light_level_for_creature(self, creature: Creature):
        "Get the current light level at the position of a creature"
        value = 0.0
        for neighbor in self.creatures.values():
            if neighbor.creature_id != creature.creature_id and neighbor.light_emission > 0.0 and creature.pos.distance_to(neighbor.pos) < neighbor.light_emission:
                value += neighbor.light_emission - creature.pos.distance_to(neighbor.pos)
        return value

    def reproduce_creatures(self):
        "If two creatures are in contact and ready to reproduce, make them have a child"
        children: set[Creature] = set()
        creatures = list(self.creatures.values())
        for i, creature1 in enumerate(creatures):
            if len(children) > 20:
                break
            for creature2 in creatures[i+1:]:
                if len(children) > 20:
                    break
                if creature1.can_repro and creature2.can_repro and creature1.rectangle.colliderect(creature2.rectangle):
                    # create the child
                    child = creature_reproduction(creature1, creature2, self.highest_creature_id, self.time)
                    # make it spawn between its parents
                    child.pos.x = (creature1.pos.x + creature2.pos.x) / 2
                    child.pos.y = (creature1.pos.y + creature2.pos.y) / 2
                    # add it to the list of newly born children
                    children.add(child)
                    # increment ID
                    self.highest_creature_id += 1
                    # update their parent
                    creature1.last_reproduction = round(time.time())
                    creature2.last_reproduction = round(time.time())
        # add every new child into the Great List of Creatures
        children_list = list(children)[:10]
        for child in children_list:
            self.creatures[child.creature_id] = child
        if len(children_list):
            print(len(children_list), "new creatures born")
    
    def move_creatures(self, pool: Pool, delta_t: int):
        arguments: list[tuple[CreatureProcessMove, int]] = []
        for creature in self.creatures.values():
            creature.update_network(self)
            arguments.append((CreatureProcessMove(creature), delta_t))
        for i in pool.imap_unordered(mp_execute_move, arguments, chunksize=40):
            self.creatures[i.creature_id] = i.apply_to_creature(self.creatures[i.creature_id])
