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

    ######################################################################
    # temps
    ######################################################################

    dt = renderer.clock.tick(FPS) / 1000.0

    ######################################################################
    # événements
    ######################################################################

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            ##################################################################
            # pause
            ##################################################################

            if event.key == pygame.K_SPACE:
                simulation.toggle_pause()

    ######################################################################
    # update simulation
    ######################################################################

    simulation.update(dt)

    ######################################################################
    # rendu
    ######################################################################

    renderer.draw(
        simulation.vehicles,
        simulation.pedestrians,
        simulation.traffic_lights,
        simulation.current_period
    )

##########################################################################
#
# fermeture
#
##########################################################################

pygame.quit()