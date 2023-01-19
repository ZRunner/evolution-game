import pygame

from . import config

UPDATE_CREATURES_ENERGIES = pygame.USEREVENT + 1
GENERATE_FOOD = pygame.USEREVENT + 2

# type and interval in ms of each enabled event
events = {
    UPDATE_CREATURES_ENERGIES: 1000,
    GENERATE_FOOD: config.FOOD_GENERATION_INTERVAL * 1000,
}
