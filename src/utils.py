from typing import Optional, TypeVar

from .creature import Creature
from .food import FoodPoint


def sign(value: float):
    return -1 if value < 0 else 0 if value == 0 else 1

T = TypeVar("T", Creature, FoodPoint)
def find_closest_entity(creature: Creature, entities: list[T]):
    "Find the closest entity from a list of entities"
    best: Optional[tuple[T, float]] = None
    for entity in entities:
        # check if the point is within the vision circle
        if best is None or entity.position.distance_to(creature.position) < min(creature.vision_distance, best[1]):
            # check if the point is within the vision cone
            angle = abs(creature.direction.angle_to(entity.position - creature.position))
            if angle > 180:
                angle = abs(360 - angle)
            if angle <= creature.vision_angle/2:
                best = (entity, entity.position.distance_to(creature.position))
    if best is not None and best[1] > creature.vision_distance:
        return None
    return best