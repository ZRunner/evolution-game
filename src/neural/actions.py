from .abc import ActionNeuron
from .. import config

class MoveXActionNeuron(ActionNeuron):
    "Moves in the X axis"
    name = "Move X"

    def act(self, creature):
        creature.own_acceleration.x = self.value

class MoveYActionNeuron(ActionNeuron):
    "Moves in the z axis"
    name = "Move Y"

    def act(self, creature):
        creature.own_acceleration.y = self.value

class EmitLightActionNeuron(ActionNeuron):
    "Emit some light visible by other creatures"
    name = "Light"

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
