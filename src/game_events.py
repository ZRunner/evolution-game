import pygame

UPDATE_CREATURES_ENERGIES = pygame.USEREVENT + 1
GENERATE_FOOD = pygame.USEREVENT + 2

events = {
    UPDATE_CREATURES_ENERGIES: 1000,
    GENERATE_FOOD: 1500,
}
