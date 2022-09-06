import time
from typing import Optional, TYPE_CHECKING

import matplotlib
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt
import numpy as np
import pygame
import pylab
from matplotlib.lines import Line2D
from pygame.font import SysFont
from pygame.surface import Surface
from pygame.time import Clock

from . import config
if TYPE_CHECKING:
    from creature import Creature
    from food import FoodPoint

matplotlib.use("Agg")

plt.rcParams.update({  # type: ignore
    # "lines.marker": "o",       # available ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')
    # "lines.linewidth": "1.8",
    # "axes.prop_cycle": plt.cycler('color', ['white']),  # line color
    # "text.color": "white",     # no text in this example
    # "axes.facecolor": "black",   # background of the figure
    # "axes.edgecolor": "lightgray",
    "axes.labelcolor": "white",  # no labels in this example
    # "axes.titlecolor": "red",
    # "axes.grid": "True",
    # "grid.linestyle": "--",      # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
    "xtick.color": "white",
    "ytick.color": "white",
    # "grid.color": "lightgray",
    "figure.facecolor": "black", # color surrounding the plot
    # "figure.edgecolor": "black",
})

class ChartData:
    "Save values of a specific metric"
    def __init__(self, name: str):
        self.name = name
        self.timestamps: list[float] = []
        self.data: list[float] = []

    @property
    def start_time(self):
        "Timestamp of the first record"
        return self.timestamps[0]

    def clear(self):
        "Delete every value"
        self.timestamps.clear()
        self.data.clear()

    def append_value(self, value: float):
        "Append a value to the records"
        self.timestamps.append(time.time())
        self.data.append(value)

    def get_axis(self, window: int = 20):
        "Get X and Y values for a given time frame"
        if len(self.timestamps) == 0:
            return ([], [])
        x = np.array(self.timestamps)
        x = x - x.min()
        min_value: float = x.max() - window
        index = x[x > min_value]
        return (index, self.data[-len(index):])


class ChartsManager:
    "Manage and display all kind of charts"

    def __init__(self, surface: Surface):
        self.surface = surface
        self.datas: dict[str, ChartData] = {
            "fps": ChartData("FPS"),
            "avg_vel": ChartData("Average Velocity"),
            "avg_acc": ChartData("Average Acceleration"),
            "creatures_count": ChartData("Creatures count"),
            "avg_size": ChartData("Average Size"),
            "avg_energy": ChartData("Average Energy"),
            "avg_life": ChartData("Average Life Percentage"),
            "foods_total": ChartData("Total food value"),
            "avg_light": ChartData("Average light"),
        }
        self.indexes = list(self.datas.keys())
        self.index = 0

        self.fig = pylab.figure(
            num=1,
            figsize=(6, 3),  # Inches
            dpi=70,          # 100 dots per inch, so the resulting buffer is 400x400 pixels
        )
        self.fig.patch.set_alpha(0.7)
        self.ax: plt.Axes = self.fig.gca()
        self.ax.patch.set_alpha(0)
    
        self.lines: list[Line2D] = self.ax.plot(np.empty(10), np.empty(10), lw=2)

        self.canvas = agg.FigureCanvasAgg(self.fig)
        self.raw_data: Optional[memoryview] = None
        self.font = SysFont("Arial", 12)

    @property
    def data_index(self):
        "Name of the currently displayed graph"
        return self.indexes[self.index]

    def get_chart(self):
        "Create data rendering, ready to be displayed"
        x, y = self.datas[self.data_index].get_axis()
        if len(x) != 0:
            self.lines[0].set_data(x, y)
            self.ax.set_xlim(left=x[0], right=x[-1])
            self.ax.set_ylim(top=max(y)*1.1, bottom=min(y)*0.9)

        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        self.raw_data = renderer.buffer_rgba()

    def draw_graph(self):
        "Draw the current graph in the bottom left corner"
        self.get_chart()
        if self.raw_data is None:
            return
        size: tuple[int, int] = self.canvas.get_width_height()
        surf = pygame.image.frombuffer(self.raw_data, size, "RGBA")
        self.surface.blit(surf, (10, config.HEIGHT - size[1] - 40))

        title_label = self.font.render(self.datas[self.data_index].name, True, pygame.Color("WHITE"))
        text_width, _ = self.font.size(self.datas[self.data_index].name)
        self.surface.blit(title_label, (size[0]/2 - text_width/2, config.HEIGHT - 30))

    def next_graph(self):
        "Increment the graph index"
        self.index = (self.index + 1) % len(self.datas)

    def previous_graph(self):
        "Decrement the graph index"
        self.index = (self.index - 1) % len(self.datas)

    def store_datas(self, clock: Clock, creatures: list["Creature"], foods: list["FoodPoint"]):
        "Store useful datas inside ChartData objects"
        # FPS
        self.datas["fps"].append_value(clock.get_fps())
        # Creatures Velocity
        if len(creatures) > 0:
            vel = [creature.vel.length() for creature in creatures]
            self.datas["avg_vel"].append_value(sum(vel)/len(vel))
            # Creatures Acceleration
            acc = [creature.acc.length() for creature in creatures]
            self.datas["avg_acc"].append_value(sum(acc)/len(acc))
            # Creatures Count
            self.datas["creatures_count"].append_value(len(creatures))
            # Creatures Sizes
            sizes = [creature.size for creature in creatures]
            self.datas["avg_size"].append_value(sum(sizes)/len(sizes))
            # Avegare Energy
            energies = [max(0, creature.energy) for creature in creatures]
            self.datas["avg_energy"].append_value(sum(energies)/len(energies))
            # Average Life percentage
            lifes = [creature.life / creature.max_life for creature in creatures]
            self.datas["avg_life"].append_value(sum(lifes)/len(lifes))
            # Total Food Value
            food = sum(point.quantity for point in foods)
            self.datas["foods_total"].append_value(food)
            # Average light emitted
            lights_e = [creature.light_emission for creature in creatures]
            self.datas["avg_light"].append_value(sum(lights_e)/len(lights_e))
        elif self.datas["creatures_count"].data[-2] > 0:
            self.datas["creatures_count"].append_value(len(creatures))
