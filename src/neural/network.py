from copy import deepcopy
from random import choice, randint, random
from typing import Optional, Union, TYPE_CHECKING
from networkx.exception import NetworkXError


from .graph import NeuralNetworkGraph
from .abc import ActionNeuron, InputNeuron, TransitionNeuron
from . import inputs, actions

if TYPE_CHECKING:
    from creature import Creature
    from context_manager import ContextManager

INPUT_NEURONS = [
    inputs.XPositionInputNeuron(),
    inputs.YPositionInputNeuron(),
    inputs.EnergyInputNeuron(),
    inputs.DigestingInputNeuron(),
    inputs.SpeedInputNeuron(),
    inputs.LifeInputNeuron(),
    inputs.LightInputNeuron(),
    inputs.FoodDistanceInputNeuron(),
    inputs.ConstantNeuron(),
    inputs.ConstantNeuron(),
    inputs.ConstantNeuron(),
    inputs.ConstantNeuron(),
    inputs.ConstantNeuron(),
    inputs.SinusoidNeuron(),
    inputs.AgeNeuron(),
]
ACTION_NEURONS = [
    actions.MoveXActionNeuron(),
    actions.MoveYActionNeuron(),
    actions.EmitLightActionNeuron(),
    actions.ReadyForReproductionActionNeuron(),
]

AnyNeuron = Union[InputNeuron, TransitionNeuron]


def merge_wires(set_1, set_2):
    "Merge 2 sets of wires, and remove any duplicated connection"
    wires: list[tuple[AnyNeuron, float, TransitionNeuron]] = []
    neurons_map: dict[str, AnyNeuron] = {}
    for wire in set_1 + set_2:
        source = neurons_map.get(wire[0].name, wire[0])
        destination: TransitionNeuron = neurons_map.get(wire[2].name, wire[2]) # type: ignore       
        if not any(w[0] == source and w[2] == destination for w in wires):
            wires.append((source, wire[1], destination))
            neurons_map[source.name] = source
            neurons_map[destination.name] = destination
    return wires

class NeuralNetworkGenerationAgent:
    "Manage generating new neural networks"

    @classmethod
    def merge(cls, parent1: "NeuralNetwork", parent2: "NeuralNetwork"):
        "Create a new neural network from 2 given parents"
        new_network = cls(0, 0)
        new_network.connections_number = randint(min(len(parent1.wires), len(parent2.wires)), max(len(parent1.wires), len(parent2.wires)))

        new_network.graph = NeuralNetworkGraph()
        new_network.wires.clear()
        # get a list of unique connections from both parents
        wires_pool = merge_wires(parent1.wires, parent2.wires)
        if new_network.connections_number > len(wires_pool):
            new_network.connections_number = len(wires_pool)

        i = 0
        while len(new_network.wires) < new_network.connections_number:
            i += 1
            j = 0
            target_connections_number = min(len(wires_pool), new_network.connections_number + 2)
            while len(new_network.wires) < target_connections_number or len(new_network.input_neurons) == 0 or len(new_network.output_neurons) == 0:
                wire = choice([w for w in wires_pool if w not in new_network.wires])
                new_network.add_wire(*wire)
                j += 1
                if j > 1000:
                    raise ValueError("Too many iterations")
            new_network.cleanup_wires()
            if i > 1000:
                raise ValueError("Too many iterations")
        
        return new_network.wires


    def __init__(self, connections: int, max_hidden_neurons: int):
        self.connections_number = connections

        self.graph = NeuralNetworkGraph()
        self.wires: list[tuple[AnyNeuron, float, TransitionNeuron]] = []
        self.hidden_neurons = [
            TransitionNeuron() for _ in range(max_hidden_neurons)
        ]
        for i, neuron in enumerate(self.hidden_neurons):
            neuron.name = f"H{i}"

        self.input_pool = deepcopy(INPUT_NEURONS)
        self.output_pool = deepcopy(ACTION_NEURONS)
    
    def generate(self):
        "Actually add more neurons into the network, and make sure we have enough connections"
        # if no connection is required, return an empty network
        if self.connections_number == 0:
            return []
        i = 0
        while len(self.wires) < self.connections_number or len(self.input_neurons) == 0 or len(self.output_neurons) == 0:
            i += 1
            if i > 1000:
                raise ValueError("Too many iterations")
            input_n: Union[InputNeuron, TransitionNeuron] = choice(
                self.input_pool + self.hidden_neurons  # type: ignore
            )
            output_n: Union[TransitionNeuron, ActionNeuron] = choice(
                self.transition_neurons + self.output_pool  # type: ignore
            )
            self.add_wire(input_n, random()*4-2, output_n)
        
        self.cleanup_wires()
        if len(self.wires) < self.connections_number:
            self.generate()
        return self.wires
    
    def cleanup_wires(self):
        "Remove useless wires"
        to_remove: set[AnyNeuron] = set()
        # remove any transition neuron with no predecessor or successor
        for neuron in self.transition_neurons:
            should_remove = True
            if len(list(self.graph.successors(neuron))) > 0:
                for pred in self.graph.predecessors(neuron):
                    if pred != neuron.name:
                        should_remove = False
            if should_remove:
                to_remove.add(neuron)
        # remove any output parent with no predecessor
        for neuron in self.output_neurons:
            try:
                preds = list(self.graph.predecessors(neuron))
            except NetworkXError as err:
                raise err
            if len(preds) == 0:
                to_remove.add(neuron)
        # Rename constant neurons
        for i, neuron in enumerate(self.input_neurons):
            if isinstance(neuron, inputs.ConstantNeuron):
                neuron.name = f"C{i}"

        for neuron in to_remove:
            self.remove_neuron(neuron)
        
        # make sure to always have at least one moving neuron
        moving_neurons = [neuron for neuron in self.output_neurons if "Move" in neuron.name]
        if len(moving_neurons) == 0 and len(self.output_neurons) > 0:
            random_neuron = choice(self.output_neurons)
            to_remove.add(random_neuron)
            self.remove_neuron(random_neuron)

        if len(to_remove) > 0:
            self.cleanup_wires()
    
    def check_connecion_exists(self, origin: AnyNeuron, direction: TransitionNeuron):
        "Check if a connection already exists between 2 neurons"
        for wire in self.wires:
            if wire[0] == origin and wire[2] == direction:
                return True
        return False 
    
    def add_wire(self, origin: AnyNeuron, weight: float, direction: TransitionNeuron):
        "Add a connection between two neurons"
        # avoid duplications
        if self.check_connecion_exists(origin, direction):
            return
        self.graph.add_neuron(origin)
        self.graph.add_neuron(direction)
        self.graph.add_wire(origin, direction, weight)
        self.wires.append((origin, weight, direction))

    def remove_neuron(self, neuron: AnyNeuron):
        "Remove a neuron from the network"
        self.graph.remove_neuron(neuron)
        self.wires = [
            wire for wire in self.wires if neuron not in wire
        ]

    @property
    def input_neurons(self):
        "List of input neurons"
        return [neuron for neuron, _, _ in self.wires if isinstance(neuron, InputNeuron)]
    
    @property
    def output_neurons(self):
        "List of output (action) neurons"
        return [neuron for _, _, neuron in self.wires if isinstance(neuron, ActionNeuron)]

    @property
    def transition_neurons(self):
        "List of transition (hidden) neurons"
        result: set[TransitionNeuron] = set()
        for neuron1, _, neuron2 in self.wires:
            for neuron in (neuron1, neuron2):
                if isinstance(neuron, TransitionNeuron) and not isinstance(neuron, ActionNeuron):
                    result.add(neuron)
        return list(result)


class NeuralNetwork:
    "Network of neurons (yes seriously)"

    @classmethod
    def from_parents(cls, parent1: "NeuralNetwork", parent2: "NeuralNetwork"):
        "Merge two neural networks to create a new one"
        new_element = cls(0, 0)
        new_element.graph = NeuralNetworkGraph()
        new_element.wires.clear()

        wires = NeuralNetworkGenerationAgent.merge(parent1, parent2)
        for wire in wires:
            new_element.add_wire(*wire)

        new_element.last_updated = set(new_element.input_neurons)
        return new_element
        

    def __init__(self, connections: int, max_hidden_neurons: int):
        self.graph = NeuralNetworkGraph()
        self.wires: list[tuple[AnyNeuron, float, TransitionNeuron]] = []

        agent = NeuralNetworkGenerationAgent(connections, max_hidden_neurons)
        wires = agent.generate()
        for wire in wires:
            self.add_wire(*wire)

        self.last_updated: set[AnyNeuron] = set(self.input_neurons)

    def add_wire(self, origin: AnyNeuron, weight: float, direction: TransitionNeuron):
        "Add a connection between two neurons"
        self.graph.add_neuron(origin)
        self.graph.add_neuron(direction)
        self.graph.add_wire(origin, direction, weight)
        self.wires.append((origin, weight, direction))

    @property
    def neurons_count(self):
        "Counts every neuron"
        return len(self.all_neurons)

    @property
    def all_neurons(self):
        "List every neuron"
        result: set[AnyNeuron] = set()
        for neuron1, _, neuron2 in self.wires:
            result.add(neuron1)
            result.add(neuron2)
        return list(result)

    @property
    def input_neurons(self):
        "List of input neurons"
        return [neuron for neuron, _, _ in self.wires if isinstance(neuron, InputNeuron)]

    @property
    def output_neurons(self):
        "List of output (action) neurons"
        return [neuron for _, _, neuron in self.wires if isinstance(neuron, ActionNeuron)]

    @property
    def transition_neurons(self):
        "List of transition (hidden) neurons"
        result: set[TransitionNeuron] = set()
        for neuron1, _, neuron2 in self.wires:
            for neuron in (neuron1, neuron2):
                if isinstance(neuron, TransitionNeuron) and not isinstance(neuron, ActionNeuron):
                    result.add(neuron)
        return list(result)

    def connections_from(self, neuron: AnyNeuron):
        "Return the list of connections starting from the given neuron"
        return [wire for wire in self.wires if wire[0] == neuron]
    
    def get_action_value(self, name: str) -> Optional[float]:
        "Get the value of an action neuron by its name"
        matching = [neuron for neuron in self.output_neurons if neuron.name == name]
        if len(matching) == 0:
            return None
        return matching[0].value
    
    def update_input(self, subject: "Creature", context: "ContextManager"):
        "Update the input neurons with the creature data"
        for neuron in self.input_neurons:
            neuron.update(subject, context)
        self.last_updated |= set(self.input_neurons)
    
    def act(self, subject: "Creature"):
        "Trigger every action"
        for neuron in self.output_neurons:
            neuron.act(subject)

    def tick(self):
        "Update every neuron"
        to_update: dict[TransitionNeuron,
                        tuple[list[AnyNeuron], list[float]]] = {}
        for neuron in self.last_updated:
            for _, weight, destination in self.connections_from(neuron):
                if destination in to_update:
                    to_update[destination][0].append(neuron)
                    to_update[destination][1].append(weight)
                else:
                    to_update[destination] = ([neuron], [weight])
        # update values
        for neuron, data in to_update.items():
            neuron.update_value(*data)
        # set for next update
        self.last_updated = set(to_update.keys())
