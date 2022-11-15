import math
from random import random
from typing import Optional
from .abc import InputNeuron, sigmoid

class XPositionInputNeuron(InputNeuron):
    "Corresponds to the X position of the creature"
    name = "X Position"

    def update(self, subject, context):
        self.value = sigmoid(subject.pos.x * 0.003)

class YPositionInputNeuron(InputNeuron):
    "Corresponds to the Y position of the creature"
    name = "Y Position"

    def update(self, subject, context):
        self.value = sigmoid(subject.pos.y * 0.003)

class EnergyInputNeuron(InputNeuron):
    "Corresponds to the energy of the creature"
    name = "Energy"

    def update(self, subject, context):
        self.value = sigmoid(subject.energy * 0.1)

class DigestingInputNeuron(InputNeuron):
    "Corresponds to the digesting quantity of the creature"
    name = "Digesting"

    def update(self, subject, context):
        self.value = sigmoid(subject.digesting * 0.02)

class SpeedInputNeuron(InputNeuron):
    "Corresponds to the speed of the creature"
    name = "Speed"

    def update(self, subject, context):
        self.value = sigmoid(subject.vel.length() * 10)

class LifeInputNeuron(InputNeuron):
    "Corresponds to the % of current life of the creature"
    name = "Life"

    def update(self, subject, context):
        self.value = subject.life / subject.max_life

class LightInputNeuron(InputNeuron):
    "Corresponds to the level of light at the position of the creature"
    name = "Light"

    def update(self, subject, context):
        self.value = sigmoid(context.get_light_level_for_creature(subject) * 0.02)

class FoodDistanceInputNeuron(InputNeuron):
    "Corresponds to the distance of the nearest food"
    name = "Food dist."

    def update(self, subject, context):
        v = context.get_food_distance_for_creature(subject)
        if v is not None and v < subject.vision:
            self.value = 1 - v / subject.vision
        else:
            self.value = -1

class ConstantNeuron(InputNeuron):
    "Corresponds to a fixed value"
    fixed_value: Optional[float] = None
    name = "Constant"

    def update(self, subject, context):
        if self.fixed_value is None:
            self.fixed_value = round(random() * 2 - 1, 3)
            self.value = self.fixed_value

class SinusoidNeuron(InputNeuron):
    "Corresponds to a value based on the time, following a sinusoid"
    name = "Sinusoid"

    def update(self, subject, context):
        self.value = math.sin((subject.birth - context.time) * 0.05)

class AgeNeuron(InputNeuron):
    "Corresponds to the creature's age in seconds"
    name = "Age"

    def update(self, subject, context):
        self.value = sigmoid((context.time - subject.birth) * 0.01)
