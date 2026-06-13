# main.py

import pygame

from settings import *
from game_data import GameData
from renderer import Renderer
from simulation import Simulation

##########################################################################
#
# INITIALISATION
#
##########################################################################

pygame.init()

game = GameData()

renderer = Renderer(game)

simulation = Simulation(game)

##########################################################################
#
# BOUCLE PRINCIPALE
#
##########################################################################

running = True

while running:

    dt = renderer.clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            
            # PAUSE
            if event.key == pygame.K_SPACE:
                simulation.toggle_pause()

    simulation.update(dt)

    renderer.draw(
        simulation.vehicles,
        simulation.pedestrians,
        simulation.traffic_lights,
        simulation.current_period
    )

pygame.quit()