from pygame import Color, Vector2
from pygame.font import SysFont
from pygame.surface import Surface

from . import config
from .context_manager import ContextManager
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

    def draw_creature_panel(self, creature: Creature, context: ContextManager):
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
        # reproduction state
        repr_label = "Yes" if creature.can_repro(context.time) else (
            "No (cooldown)" if creature.last_reproduction + config.CREATURE_REPRO_COOLDOWN > context.time else "No (disabled neuron)"
            )
        damage_label = "Yes" if creature.can_attack(context.time) else (
            "No (cooldown)" if creature.last_damage_action + config.CREATURE_ATTACK_COOLDOWN > context.time else "No (disabled neuron)"
            )
        # Info
        texts = [
            f"Generation {creature.generation}",
            f"Size: {creature.size}",
            f"Age: {context.time - creature.birth:.0f}s",
            f"Position: ({creature.position.x:.0f}, {creature.position.y:.0f})",
            f"Speed: {creature.velocity*1000:.1f}p/s",
            f"Acceleration: {creature.acceleration*1000:.1f}p/s²",
            f"Direction: {creature.direction.as_polar()[1]:.0f}° ({creature.direction.x:.3f}, {creature.direction.y:.3f})",
            f"Life: {creature.life} / {creature.max_life} (regen cost: {creature.life_regen_cost})",
            f"Energy: {creature.energy:.1f}",
            f"Digestion: {creature.digesting} (efficiency: {creature.digestion_efficiency}, speed: {creature.digestion_speed})",
            f"Vision: {creature.vision_distance:.0f}p - {creature.vision_angle}°",
            f"Light emission: {creature.light_emission}",
            f"Ready for reproduction: {repr_label}",
            f"Max damage: {creature.max_damage}",
            f"Ready to inflict damage: {damage_label}",
        ]
        for i, text in enumerate(texts):
            render = self.font.render(text, True, "white")
            self.surface.blit(render, Vector2(self.rect.topleft) + Vector2(20, 60 + 20*i))
        # Neural network
        creature.network.graph.draw(self.surface)
