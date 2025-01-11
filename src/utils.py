from pygame import Vector2


def sign(value: float):
    "Return the sign of a number (-1, 0, 1)"
    return -1 if value < 0 else 0 if value == 0 else 1

def get_toroidal_distance(a: Vector2, b: Vector2, width: int, height: int) -> float:
    "Return the distance between two points in a toroidal space"
    dx = abs(b.x - a.x) % width
    dy = abs(b.y - a.y) % height
    return (dx ** 2 + dy ** 2) ** 0.5
