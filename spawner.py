# spawner.py

import random

from settings import *
from game_data import HOME, WORKPLACE, CITY_CENTER, ZONE_SYMBOLS
from vehicle import Vehicle
from pedestrian import Pedestrian


class Spawner:
    def __init__(self, game, vehicles, pedestrians):
        self.game = game
        self.vehicles = vehicles
        self.pedestrians = pedestrians

        self.accu_vehicle = 0.0
        self.accu_pedestrian = 0.0

    def update(self, dt, current_period):
        intensity = TRAFFIC_INTENSITY[current_period] * self.game.get_flow_factor()

        self.accu_vehicle += intensity * dt
        self.accu_pedestrian += (intensity * 0.45) * dt

        while self.accu_vehicle >= 1.0:
            self.spawn_vehicle(current_period)
            self.accu_vehicle -= 1.0

        while self.accu_pedestrian >= 1.0:
            self.spawn_pedestrian(current_period)
            self.accu_pedestrian -= 1.0

    def spawn_vehicle(self, current_period):
        if len(self.vehicles) >= MAX_VEHICLES:
            return

        spawn = self.game.choose_spawn("vehicle")

        if (
            spawn is None
            or self.game.get_density(*spawn) >= MAX_DENSITY
            or not self.game.is_vehicle_tile_available(spawn)
        ):
            return

        missions = self._vehicle_missions(current_period, spawn)

        if not missions:
            return

        vehicle = Vehicle(self.game, spawn, missions)

        if not self.game.reserve_vehicle_tile(spawn, vehicle):
            return

        self.vehicles.append(vehicle)

    def spawn_pedestrian(self, current_period):
        if len(self.pedestrians) >= MAX_PEDESTRIANS:
            return

        spawn_zones = self._pedestrian_spawn_zones(current_period)
        spawn = self.game.choose_spawn("pedestrian", spawn_zones)

        if spawn is None:
            return

        missions = self._pedestrian_missions(current_period, spawn)

        if not missions:
            return

        self.pedestrians.append(Pedestrian(self.game, spawn, missions))

    def _vehicle_missions(self, current_period, spawn):
        missions = []
        current_position = spawn

        if current_period == MORNING:
            zone_choices = [
                [WORKPLACE],
                [WORKPLACE, CITY_CENTER],
            ]

        elif current_period == AFTERNOON:
            zone_choices = [
                [HOME, WORKPLACE, CITY_CENTER],
                [HOME, WORKPLACE, CITY_CENTER],
            ]

        elif current_period == EVENING:
            zone_choices = [
                [WORKPLACE, CITY_CENTER],
                [HOME],
            ]

        else:
            zone_choices = [
                [HOME, WORKPLACE, CITY_CENTER],
                [HOME, WORKPLACE, CITY_CENTER],
            ]

        for zones in zone_choices:
            target = self.game.choose_reachable_access(
                current_position,
                zones,
                "vehicle",
                missions
            )
            self._append_target(missions, target)

            if target is not None:
                current_position = target

        exit_target = self.game.choose_reachable_exit(
            current_position,
            "vehicle",
            missions
        )
        self._append_target(missions, exit_target)

        if exit_target is not None:
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

        return missions[:3]

    def _append_target(self, missions, target):
        if target is None:
            return

        if target in missions:
            return

        missions.append(target)

    def _pedestrian_spawn_zones(self, current_period):
        if current_period == MORNING:
            return [HOME]

        if current_period == AFTERNOON:
            return [WORKPLACE, CITY_CENTER, HOME]

        return [WORKPLACE, CITY_CENTER]

    def _pedestrian_missions(self, current_period, spawn):
        missions = []
        current_position = spawn

        if current_period == MORNING:
            target = self.game.choose_reachable_access(
                current_position,
                [WORKPLACE, CITY_CENTER],
                "pedestrian",
                missions
            )

        elif current_period == AFTERNOON:
            target = self.game.choose_reachable_access(
                current_position,
                [HOME, WORKPLACE, CITY_CENTER],
                "pedestrian",
                missions
            )

        elif current_period == EVENING:
            if random.random() < 0.75:
                target = self.game.choose_reachable_access(
                    current_position,
                    [HOME],
                    "pedestrian",
                    missions
                )
            else:
                target = self.game.choose_reachable_access(
                    current_position,
                    ZONE_SYMBOLS,
                    "pedestrian",
                    missions
                )

        else:
            target = self.game.choose_reachable_access(
                current_position,
                ZONE_SYMBOLS,
                "pedestrian",
                missions
            )

        if target is None:
            target = self.game.choose_reachable_access(
                current_position,
                ZONE_SYMBOLS,
                "pedestrian",
                missions
            )

        if target:
            missions.append(target)
            current_position = target

        if current_period != MORNING and random.random() < 0.25:
            exit_target = self.game.choose_reachable_access(
                current_position,
                ZONE_SYMBOLS,
                "pedestrian",
                missions
            )

            if exit_target and (not missions or missions[-1] != exit_target):
                missions.append(exit_target)

        return missions
