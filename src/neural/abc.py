from typing import Union, TYPE_CHECKING
from math import exp


def sigmoid(value: float):
    "Calculate the sigmoid of a float (between -1 and 1)"
    try:
        return 2/ (1 + exp(-value)) - 1
    except OverflowError:
        return -1.0 if value < 0 else 1.0


if TYPE_CHECKING:
    from creature import Creature
    from context_manager import ContextManager


class TransitionNeuron:
    "Basic neuron"

    name = "H"

    def __init__(self):
        self.value = 0.0

    def update_value(self,
                     previous_neurons: list[Union["TransitionNeuron", "InputNeuron"]],
                     weights: list[float]
                     ):
        "Update the neuron value"
        self.value = sum(neuron.value * weight for neuron,
                         weight in zip(previous_neurons, weights))
        self.value = sigmoid(self.value)


class InputNeuron:
    "Neuron used as input"

    name = "I"

    def __init__(self):
        self.value = 0.0

    def update(self, subject: "Creature", context: "ContextManager"):
        "Update the input value from the given subject"
        raise NotImplementedError


class ActionNeuron(TransitionNeuron):
    "Neuron used as an output"

    name = "A"

    def act(self, creature: "Creature"):
        "Execute an action on a creature based on the current neuron value"
        raise NotImplementedError
