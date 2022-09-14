from multiprocessing import Pool
from typing import Optional

import pygame

from src import config
from src.charts import ChartsManager
from src.context_manager import ContextManager
from src.creature import Creature
from src.creatures_panel import PanelsManager
from src.game_events import GENERATE_FOOD, UPDATE_CREATURES_ENERGIES, events
from src.interface import display_fps

pygame.init()

def detect_selection(click: pygame.Vector2, creatures: list[Creature]):
    "Delect on which creature the user clicked"
    potentials: list[tuple[float, int]] = []
    for creature in creatures:
        distance = pygame.Vector2(creature.rectangle.center).distance_to(click)
        if distance < 5 + creature.size:
            potentials.append((distance, creature.creature_id))
    if potentials:
        return sorted(potentials)[0][1]
    return None


# pylint: disable=too-many-branches
def main():
    "Run everything"
    clock = pygame.time.Clock()
    pygame.display.set_caption('Evolution Game')
    window_surface = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    font = pygame.font.SysFont("Arial", 14)

    context = ContextManager()

    is_running = True
    is_pause = False
    show_graphs = False
    delta_t = 0 # ms
    selected_creature_id: Optional[int] = None
    charts = ChartsManager(window_surface)
    panels = PanelsManager(window_surface)

    # generate food
    for _ in range(config.INITIAL_FOOD_QUANTITY):
        context.generate_food()

    # launch events
    for event_type, frequency in events.items():
        pygame.time.set_timer(event_type, frequency)

    with Pool() as pool:
        while is_running:
            for event in pygame.event.get():
                # name = pygame.event.event_name(event.type)
                # if "Window" not in name and "MouseMotion" not in name:
                #     print("EVENT", pygame.event.event_name(event.type))
                if event.type == pygame.QUIT:
                    is_running = False
                    pygame.quit()
                    pool.close()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        is_pause = not is_pause
                    if event.key == pygame.K_g:
                        show_graphs = not show_graphs
                    if event.key == pygame.K_LEFT:
                        charts.previous_graph()
                    if event.key == pygame.K_RIGHT:
                        charts.next_graph()
                    if event.key == pygame.K_ESCAPE and selected_creature_id:
                        selected_creature_id = None
                if event.type == pygame.MOUSEBUTTONUP:
                    click = pygame.Vector2(event.pos)
                    selected_creature_id = detect_selection(click, context.creatures.values())
                if event.type == UPDATE_CREATURES_ENERGIES and not is_pause:
                    context.update_creatures_energies()
                if event.type == GENERATE_FOOD and not is_pause:
                    context.generate_food()

            window_surface.fill((0, 0, 0))

            # draw lights
            for entity in context.creatures.values():
                entity.draw_light_circle(window_surface)


            if not is_pause:
                context.move_creatures(pool, delta_t)

            for entity in context.creatures.values():
                if not is_pause:
                    context.detect_creature_eating(entity)
                is_selected = entity.creature_id == selected_creature_id
                entity.draw(window_surface, is_selected=is_selected)

            for generator in context.food_generators:
                generator.draw(window_surface)

            for food_point in context.foods:
                food_point.draw(window_surface)

            display_fps(window_surface, font, clock)

            if selected_creature_id is not None:
                if creature := next(
                    (c for c in context.creatures.values() if c.creature_id == selected_creature_id),
                        None):
                    panels.draw_creature_panel(creature)
                else:
                    selected_creature_id = None

            if show_graphs:
                charts.draw_graph()

            if not is_pause:
                # save datas for charts
                charts.store_datas(clock, context.creatures.values(), context.foods)
                # make children or smth
                context.reproduce_creatures()

            pygame.display.update()
            delta_t = clock.tick(config.FPS)

if __name__ == '__main__':
    main()
