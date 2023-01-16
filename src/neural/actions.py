from .abc import ActionNeuron
from .. import config

class MoveActionNeuron(ActionNeuron):
    "Create an acceleration movement for the creature"
    name = "Acceleration"

    def act(self, creature):
        creature.acceleration_from_neuron = self.value

class RotateActionNeuron(ActionNeuron):
    "Rotate the creature direction"
    name = "Rotation"

    def act(self, creature):
        creature.rotation_from_neuron = self.value / 20

class EmitLightActionNeuron(ActionNeuron):
    "Emit some light visible by other creatures"
    name = "Light e."

    def act(self, creature):
        creature.light_emission = round(
            max(0,
                (self.value - 0.15) * config.CREATURE_MAX_LIGHT_DISTANCE_EMISSION
            )
        )

class ReadyForReproductionActionNeuron(ActionNeuron):
    "Boolean telling if the creature is ready to reproduce"
    name = "Reproduction"

    def act(self, creature):
        creature.ready_for_reproduction = self.value >= config.CREATURE_MIN_REPRODUCTION_STATE
