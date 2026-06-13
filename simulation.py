# simulation.py

import random

from settings import *
from game_data import HOME, WORKPLACE, CITY_CENTER
from spawner import Spawner
from traffic_light import TrafficLight


class Simulation:
    def __init__(self, game):
        self.game = game

        self.vehicles = []
        self.pedestrians = []

        self.traffic_lights = [
            TrafficLight(position)
            for position in self.game.traffic_lights
        ]
        self.game.set_traffic_lights(self.traffic_lights)

        self.spawner = Spawner(
            self.game,
            self.vehicles,
            self.pedestrians
        )

        self.period_index = 0
        self.current_period = DAY_PERIODS[self.period_index]
        self.period_timer = 0.0
        self.waiting_for_cycle_restart = False

        self.paused = False

    def toggle_pause(self):
        self.paused = not self.paused

    def update(self, dt):
        if self.paused:
            return

        self.update_period(dt)

        for light in self.traffic_lights:
            light.update(dt)

        if not self.waiting_for_cycle_restart:
            self.spawner.update(dt, self.current_period)

        self.update_density()

        for vehicle in self.vehicles[:]:
            vehicle.update(dt)

            if vehicle.is_finished():
                self.vehicles.remove(vehicle)

        self.update_density()

        for pedestrian in self.pedestrians[:]:
            pedestrian.update(dt)

            if pedestrian.is_finished():
                self.pedestrians.remove(pedestrian)

        self.update_density()

    def update_period(self, dt):
        if self.waiting_for_cycle_restart:
            if not self.has_active_entities():
                self.advance_period()

            return

        self.period_timer += dt

        if self.period_timer < DAY_PERIOD_DURATION:
            return

        self.period_timer -= DAY_PERIOD_DURATION

        if self.current_period == EVENING and self.has_active_entities():
            self.waiting_for_cycle_restart = True
            self.send_everyone_home()
            return

        self.advance_period()

    def advance_period(self):
        self.period_index = (self.period_index + 1) % len(DAY_PERIODS)
        self.current_period = DAY_PERIODS[self.period_index]
        self.period_timer = 0.0
        self.waiting_for_cycle_restart = False

        if self.current_period == EVENING:
            self.send_everyone_home()

    def has_active_entities(self):
        return bool(self.vehicles or self.pedestrians)

    def send_everyone_home(self):
        for vehicle in self.vehicles:
            missions = []
            current_position = vehicle.get_current_tile()

            home = self.game.choose_reachable_access(
                current_position,
                [HOME],
                "vehicle",
                missions
            )

            if home:
                missions.append(home)
                current_position = home

            if random.random() < 0.35:
                second_home = self.game.choose_reachable_access(
                    current_position,
                    [HOME],
                    "vehicle",
                    missions
                )

                if second_home and second_home != home:
                    missions.append(second_home)
                    current_position = second_home

            exit_target = self.game.choose_reachable_exit(
                current_position,
                "vehicle",
                missions
            )

            if exit_target and exit_target not in missions:
                missions.append(exit_target)
                current_position = exit_target

            while len(missions) < 3:
                fallback = self.game.choose_reachable_road(
                    current_position,
                    missions
                )

                if fallback is None:
                    fallback = current_position

                missions.append(fallback)
                current_position = fallback

            if missions:
                vehicle.set_missions(missions[:3])

        for pedestrian in self.pedestrians:
            current_position = pedestrian.get_current_tile()

            if random.random() < 0.75:
                target = self.game.choose_reachable_access(
                    current_position,
                    [HOME],
                    "pedestrian"
                )
            else:
                target = self.game.choose_reachable_access(
                    current_position,
                    [HOME, WORKPLACE, CITY_CENTER],
                    "pedestrian"
                )

            if target:
                pedestrian.set_missions([target])

    def update_density(self):
        self.game.clear_traffic_state()

        for vehicle in self.vehicles:
            self.game.register_vehicle(vehicle)

        for pedestrian in self.pedestrians:
            self.game.register_pedestrian(pedestrian)
