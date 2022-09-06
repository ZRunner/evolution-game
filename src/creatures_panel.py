# from grapy import Graph

from pygame import Color, Vector2
from pygame.font import SysFont
from pygame.surface import Surface

from .creature import Creature

class PanelsManager:
    "Display contextual info on the right side of the window"

    def __init__(self, surface: Surface):
        self.surface = surface
        self.title_font = SysFont("Arial", 14)
        self.font = SysFont("Arial", 12)

        win_x, win_y = surface.get_size()
        self.surf = Surface((300, win_y))
        self.surf.fill(Color("#DDDDFF"))
        self.surf.set_alpha(80)
        self.rect = self.surf.get_rect(center=(win_x - self.surf.get_size()[0]/2, win_y/2))

    def draw_creature_panel(self, creature: Creature):
        "Draw info about a given creature"
        self.surface.blit(self.surf, self.rect)
        # icon
        icon_surface = Surface((round(creature.size*1.7+2), )*2)
        icon_surface.fill(creature.color)
        icon_rect = icon_surface.get_rect(
            center=((self.rect.topleft[0] + 80, self.rect.topleft[1] + 33))
        )
        self.surface.blit(icon_surface, icon_rect)
        # ID
        text = self.title_font.render(f"Creature #{creature.creature_id}", True, "white")
        self.surface.blit(text, Vector2(self.rect.topleft) + Vector2(100, 25))
        # Info
        texts = [
            f"Generation {creature.generation}",
            f"Size: {creature.size}",
            f"Position: ({creature.pos.x:.0f}, {creature.pos.y:.0f})",
            f"Speed: {creature.vel.length()*1000:.1f}p/s",
            f"Acceleration: {creature.acc.length()*1000:.1f}p/s²",
            f"Life: {creature.life} / {creature.max_life} (regen cost: {creature.life_regen_cost})",
            f"Energy: {creature.energy:.1f}",
            f"Digestion: {creature.digesting} (efficiency: {creature.digestion_efficiency}, speed: {creature.digestion_speed})",
            f"Vision: {creature.vision:.0f}",
            f"Light emission: {creature.light_emission}"
        ]
        for i, text in enumerate(texts):
            render = self.font.render(text, True, "white")
            self.surface.blit(render, Vector2(self.rect.topleft) + Vector2(20, 60 + 20*i))
        # Neural network
        creature.network.graph.draw(self.surface)
