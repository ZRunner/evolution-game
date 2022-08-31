from typing import Optional
from .creature import Creature
from .food import FoodGenerator, FoodPoint
from . import config

class ContextManager:

    def __init__(self):
        self.creatures: list[Creature] = [Creature(i) for i in range(config.CREATURES_COUNT)]
        self.food_generators: list[FoodGenerator] = [
            FoodGenerator(None, 160, 0.7),
            FoodGenerator(None, 80, 0.4),
            FoodGenerator(None, 40, 0.3),
        ]
        self.foods: list[FoodPoint] = []
    
    def update_creatures_energies(self):
        "Update creatures energies and life, and remove killed ones"
        to_die: list[Creature] = []
        for entity in self.creatures:
            entity.update_energy()
            if entity.life <= 0:
                to_die.append(entity)
        for entity in to_die:
            self.creatures.remove(entity)
    
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
        best: Optional[float] = None
        for food in self.foods:
            if best is None or food.position.distance_to(creature.pos) < best:
                best = food.position.distance_to(creature.pos)
        return best
    
    def get_light_level_for_creature(self, creature: Creature):
        return 0.0