from typing import Iterator, Optional, Union

import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt
import networkx as nx
import pygame
import pylab
from pygame.font import SysFont
from pygame.surface import Surface


from .abc import ActionNeuron, InputNeuron, TransitionNeuron
AnyNeuron = Union[InputNeuron, TransitionNeuron]

class NeuralNetworkGraph:
    "Some graph thing"

    def __init__(self):
        self.graph = nx.DiGraph()
        self.font = SysFont("Arial", 13)
        self.canvas_size: tuple[int, int]
        self.raw_data: Optional[memoryview] = None
        self.pos: Optional[dict] = None
        self.viewLim: Optional[tuple[tuple[float, float], tuple[float, float]]] = None
        self.neurons_map: dict[str, AnyNeuron] = {}

    def add_neuron(self, neuron: AnyNeuron):
        "Add a neuron to the graph"
        if isinstance(neuron, InputNeuron):
            self.graph.add_node(neuron.name, color="orange")
        elif isinstance(neuron, ActionNeuron):
            self.graph.add_node(neuron.name, color="green")
        else:
            self.graph.add_node(neuron.name)
        self.neurons_map[neuron.name] = neuron
        self.pos = None

    def add_wire(self, origin: AnyNeuron, direction: TransitionNeuron, weight: float):
        "Add a connection between two neurons"
        self.graph.add_edge(origin.name, direction.name, weight=weight)
        self.pos = None

    def remove_neuron(self, neuron: AnyNeuron):
        "Remove a neuron from the graph"
        self.graph.remove_node(neuron.name)
        del self.neurons_map[neuron.name]
        self.pos = None

    def predecessors(self, neuron: AnyNeuron) -> Iterator[AnyNeuron]:
        "Returns an iterator over predecessor nodes of n."
        return self.graph.predecessors(neuron.name)
    
    def successors(self, neuron: AnyNeuron) -> Iterator[AnyNeuron]:
        "Returns an iterator over successors nodes of n."
        return self.graph.successors(neuron.name)

    def add_node(self, name: str, parent: str):
        "Add a node to the graph"
        self.graph.add_edge(parent, name)

    def generate_canvas(self):
        "Generate the canvas for later use"
        if self.pos is None:
            # self.pos = nx.kamada_kawai_layout(self.graph)
            # self.pos = nx.planar_layout(self.graph)
            self.pos = nx.spring_layout(self.graph, k=0.9)
        fig = pylab.figure(
            # num=2,
            figsize=(3, 2),  # Inches
            dpi=100,
            tight_layout = {'pad': 0}
        )
        ax: plt.Axes = fig.gca()  # pylint: disable=invalid-name
        canvas = agg.FigureCanvasAgg(fig)
        edges: list[dict[str, float]] = list(self.graph.edges().values())  # type: ignore
        nx.draw(
            self.graph,
            pos=self.pos,
            with_labels=True,
            ax=ax,
            node_color=[
                node.get("color", "gray")
                for node in self.graph.nodes.values()
            ],
            edge_color=[
                "red" if edge["weight"] < 0 else "blue"
                for edge in edges
            ],
            width=[
                abs(edge["weight"] * 1.9) + 0.1
                for edge in edges
            ],
            font_size=8,
            # font_color="white",
        )
        canvas.draw()
        renderer = canvas.get_renderer()
        self.raw_data = renderer.buffer_rgba()
        self.canvas_size = canvas.get_width_height()
        self.viewLim = ax.viewLim.intervalx, ax.viewLim.intervaly
        plt.close(fig)

    def draw(self, surface: Surface):
        "Draw the graph"
        if len(self.graph.nodes) == 0:
            return
        if self.raw_data is None or self.pos is None:
            self.generate_canvas()
        if self.raw_data is None:
            return
        size = self.canvas_size
        surf = pygame.image.frombuffer(self.raw_data, size, "RGBA")
        s_width, s_height = surface.get_size()
        surface.blit(surf, (s_width - size[0], s_height - size[1] - 20))
        self.detect_tooltip(surface)

    def detect_tooltip(self, surface: Surface):
        "Draw tooltips over the graph is mouse is over a neuron"
        if self.viewLim is None or self.pos is None:
            return
        # mouse position
        mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
        # width of the plot
        plot_width = self.viewLim[0][1] - self.viewLim[0][0]
        # height of the plot
        plot_height = self.viewLim[1][1] - self.viewLim[1][0]
        # width and height of the window
        screen_width, screen_height = surface.get_size()
        # width and height of the canvas
        canvas_width, canvas_height = self.canvas_size
        # x and y coo of the canvas
        canvas_x, canvas_y = screen_width - canvas_width, screen_height - canvas_height - 20
        # x and y coo of the mouse relatively to the canvas
        mouse_rel_x = mouse_pos_x - canvas_x
        mouse_rel_y = mouse_pos_y - canvas_y
        for name, position in self.pos.items():
            # uniformized position (between 0 and 1)
            p = (position - [self.viewLim[0][0], self.viewLim[1][0]]) / [plot_width, plot_height]
            # scaled position (between 0 and X)
            p *= self.canvas_size
            # reverse Y axis
            p[1] = p[1] * -1 + canvas_height
            if abs(mouse_rel_x - p[0]) < 10 and abs(mouse_rel_y - p[1]) < 10:
                self.draw_tooltip(surface, name)
    
    def draw_tooltip(self, surface: Surface, name: str):
        "Actually draw a tooltip where needed"
        raw_value = self.neurons_map[name].value
        title_label = name
        value_label = f"{raw_value:.2f}"
        length = max(len(title_label), len(value_label)) + 4
        title_label = title_label.center(length)
        value_label = value_label.center(length)
        # mouse position
        mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
        # render neuron name
        label = self.font.render(title_label, True, pygame.Color("WHITE"), pygame.Color("#262626"))
        label_width, _ = self.font.size(title_label)
        surface.blit(label, (mouse_pos_x - label_width/2, mouse_pos_y - 30))
        # render neuron value
        value = self.font.render(value_label, True, pygame.Color("WHITE"), pygame.Color("#262626"))
        value_width, _ = self.font.size(value_label)
        surface.blit(value, (mouse_pos_x - value_width/2, mouse_pos_y - 15))
