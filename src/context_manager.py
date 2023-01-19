from multiprocessing.pool import Pool

from . import config
from .creature import Creature, creature_reproduction
from .food import FoodGenerator, FoodPoint
from .mp_utils import CreatureProcessMove, mp_execute_move
from .utils import find_closest_entity


class ContextManager:

    def __init__(self):
        self.creatures: dict[int, Creature] = {i: Creature(i, 0, 0.0) for i in range(config.INITIAL_CREATURES_COUNT)}
        self.highest_creature_id = config.INITIAL_CREATURES_COUNT - 1
        self.food_generators: list[FoodGenerator] = [
            FoodGenerator(None, 160, 0.8),
            FoodGenerator(None, 80, 0.5),
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
        if to_die:
            print(len(to_die), "creature(s) died")
    
    def generate_initial_food(self):
        "Generate initial food points"
        for generator in self.food_generators:
            for _ in range(config.INITIAL_FOOD_QUANTITY):
                if food := generator.tick():
                    self.foods.append(food)
    
    def generate_food(self):
        "Generate food points around food generators"
        for generator in self.food_generators:
            for _ in range(config.MAX_FOOD_GENERATED_PER_CYCLE):
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
        if best := find_closest_entity(creature, self.foods):
            return best[1]
        return None

    def get_light_level_for_creature(self, creature: Creature):
        "Get the current light level at the position of a creature"
        value = 0.0
        for neighbor in self.creatures.values():
            if neighbor.creature_id != creature.creature_id and neighbor.light_emission > 0.0 and creature.position.distance_to(neighbor.position) < neighbor.light_emission:
                value += neighbor.light_emission - creature.position.distance_to(neighbor.position)
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
                    # set the initial life of the child to 70%
                    child.life = round(child.max_life * config.CHILD_INITIAL_LIFE_PERCENT)
        # add every new child into the Great List of Creatures
        children_list = list(children)[:10]
        for child in children_list:
            self.creatures[child.creature_id] = child
        if len(children_list):
            print(len(children_list), "new creatures born")

    def attack_creatures(self):
        "If one creature is ready to attack, make it attack the nearest creature"
        creatures = list(self.creatures.values())
        for creature in creatures:
            if creature.max_damage > 0 and creature.can_attack(self.time):
                victim = find_closest_entity(creature, [
                    c for c in creatures if c.creature_id != creature.creature_id
                ])
                if victim is not None:
                    victim = victim[0]
                    distance = 1 - creature.position.distance_to(victim.position)/creature.vision_distance
                    damages = round(creature.max_damage * distance)
                    if damages != 0:
                        victim.receive_damages(damages)
                        creature.last_damage_action = self.time
                        victim.last_damage_received = self.time

    def move_creatures(self, pool: Pool, delta_t: int):
        arguments: list[tuple[CreatureProcessMove, int]] = []
        for creature in self.creatures.values():
            creature.update_network(self)
            arguments.append((CreatureProcessMove(creature), delta_t))
        for i in pool.imap_unordered(mp_execute_move, arguments, chunksize=40):
            i.apply_to_creature(self.creatures[i.creature_id])
