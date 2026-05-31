# game_data.py

from collections import deque
import random

import numpy as np

from map_data import CITY_MAP
from settings import *


HOME = "H"
WORKPLACE = "W"
CITY_CENTER = "C"
ZONE_SYMBOLS = (HOME, WORKPLACE, CITY_CENTER)

VEHICLE_DIRECTIONS = {
    ROAD_RIGHT: (1, 0),
    ROAD_LEFT: (-1, 0),
    ROAD_UP: (0, 1),
    ROAD_DOWN: (0, -1),
}


class GameData:
    """
    Stocke la ville et les donnees partagees par les agents.

    C'est volontairement le point central pour les voisins, les distance maps,
    la densite et les acces aux zones urbaines, comme dans la logique simstore.
    """

    def __init__(self):
        self.map, self.mapW, self.mapH = self._create_map(CITY_MAP)

        self.density = np.zeros((self.mapW, self.mapH), dtype=np.int32)
        self.vehicle_occupancy = {}
        self.vehicle_reservations = {}
        self.pedestrian_occupancy = {}
        self.distance_cache = {}

        self.spawns = self._find_tiles(SPAWN)
        self.exits = self._find_tiles(EXIT)
        self.crossroads = self._find_tiles(CROSSROAD)
        self.traffic_lights = self._find_tiles(TRAFFIC_LIGHT)
        self.pedestrian_crossings = self._find_tiles(PEDESTRIAN_WAY)

        self.homes = self._find_tiles(HOME)
        self.workplaces = self._find_tiles(WORKPLACE)
        self.city_centers = self._find_tiles(CITY_CENTER)

        self.roads = self._find_roads()
        self.walkable_tiles = self._find_walkable_tiles()

        self.vehicle_access = {
            HOME: self._find_access_points(HOME, "vehicle"),
            WORKPLACE: self._find_access_points(WORKPLACE, "vehicle"),
            CITY_CENTER: self._find_access_points(CITY_CENTER, "vehicle"),
        }

        self.pedestrian_access = {
            HOME: self._find_access_points(HOME, "pedestrian"),
            WORKPLACE: self._find_access_points(WORKPLACE, "pedestrian"),
            CITY_CENTER: self._find_access_points(CITY_CENTER, "pedestrian"),
        }

        self.traffic_light_objects = []

    def _create_map(self, text):
        rows = text.strip("\n").splitlines()
        rows = [line.strip().replace(".", "") for line in rows if line.strip()]

        for line in rows:
            if len(line) != len(rows[0]):
                raise ValueError("Erreur : lignes de tailles differentes")

        rows.reverse()
        grid = [[c for c in row] for row in rows]
        array = np.array(grid, dtype="U1").transpose()
        width, height = array.shape

        return array, width, height

    def in_bounds(self, x, y):
        return 0 <= x < self.mapW and 0 <= y < self.mapH

    def _find_tiles(self, symbol):
        positions = []

        for x in range(self.mapW):
            for y in range(self.mapH):
                if self.map[x, y] == symbol:
                    positions.append((x, y))

        return positions

    def _find_roads(self):
        return [
            (x, y)
            for x in range(self.mapW)
            for y in range(self.mapH)
            if self.is_road(x, y)
        ]

    def _find_walkable_tiles(self):
        return [
            (x, y)
            for x in range(self.mapW)
            for y in range(self.mapH)
            if self.is_walkable(x, y)
        ]

    def _neighbours4(self, x, y):
        return [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

    def _is_pedestrian_way_tile(self, x, y):
        return self.in_bounds(x, y) and self.map[x, y] == PEDESTRIAN_WAY

    def _has_horizontal_pedestrian_way_pair(self, x, y):
        return (
            self._is_pedestrian_way_tile(x - 1, y)
            and self._is_pedestrian_way_tile(x + 1, y)
        )

    def _has_vertical_pedestrian_way_pair(self, x, y):
        return (
            self._is_pedestrian_way_tile(x, y - 1)
            and self._is_pedestrian_way_tile(x, y + 1)
        )

    def _has_pedestrian_way_pair(self, x, y):
        return (
            self._has_horizontal_pedestrian_way_pair(x, y)
            or self._has_vertical_pedestrian_way_pair(x, y)
        )

    def is_road(self, x, y):
        if not self.in_bounds(x, y):
            return False

        return self.map[x, y] in [
            ROAD_RIGHT,
            ROAD_LEFT,
            ROAD_UP,
            ROAD_DOWN,
            CROSSROAD,
            SPAWN,
            EXIT,
            TRAFFIC_LIGHT,
            PEDESTRIAN_WAY,
        ]

    def is_crossing_tile(self, x, y):
        if not self.in_bounds(x, y):
            return False

        tile = self.map[x, y]

        if tile == PEDESTRIAN_WAY:
            return True

        if not self.is_road(x, y):
            return False

        return self._has_pedestrian_way_pair(x, y)

    def is_walkable(self, x, y):
        if not self.in_bounds(x, y):
            return False

        tile = self.map[x, y]

        return tile in (EMPTY, PEDESTRIAN_WAY) or self.is_crossing_tile(x, y)

    def is_pedestrian_spawn_tile(self, x, y):
        if not self.in_bounds(x, y):
            return False

        return self.map[x, y] == EMPTY

    def get_crossing_axis(self, x, y):
        if not self.is_crossing_tile(x, y):
            return "horizontal"

        if self.map[x, y] == PEDESTRIAN_WAY:
            horizontal_score = int(self.is_road(x - 1, y)) + int(self.is_road(x + 1, y))
            vertical_score = int(self.is_road(x, y - 1)) + int(self.is_road(x, y + 1))

            if vertical_score > horizontal_score:
                return "vertical"

            return "horizontal"

        if self._has_horizontal_pedestrian_way_pair(x, y):
            return "horizontal"

        if self._has_vertical_pedestrian_way_pair(x, y):
            return "vertical"

        def pedestrian_corridor(nx, ny):
            if not self.in_bounds(nx, ny):
                return False

            return self.map[nx, ny] in (PEDESTRIAN_WAY, EMPTY)

        horizontal_score = int(pedestrian_corridor(x - 1, y)) + int(pedestrian_corridor(x + 1, y))
        vertical_score = int(pedestrian_corridor(x, y - 1)) + int(pedestrian_corridor(x, y + 1))

        if vertical_score > horizontal_score:
            return "vertical"

        return "horizontal"

    def get_neighbours(self, x, y, profile):
        if profile == "vehicle":
            return self.get_vehicle_neighbours(x, y)

        return [
            (nx, ny)
            for nx, ny in self._neighbours4(x, y)
            if self.is_walkable(nx, ny)
        ]

    def get_vehicle_neighbours(self, x, y):
        if not self.is_road(x, y):
            return []

        tile = self.map[x, y]

        if tile in VEHICLE_DIRECTIONS:
            dx, dy = VEHICLE_DIRECTIONS[tile]
            candidate = (x + dx, y + dy)

            if self._can_vehicle_move((x, y), candidate):
                return [candidate]

            return []

        if tile == EXIT:
            return []

        return [
            (nx, ny)
            for nx, ny in self._neighbours4(x, y)
            if self._can_vehicle_move((x, y), (nx, ny))
        ]

    def get_vehicle_predecessors(self, x, y):
        if not self.is_road(x, y):
            return []

        target = (x, y)

        return [
            (nx, ny)
            for nx, ny in self._neighbours4(x, y)
            if self.is_road(nx, ny) and target in self.get_vehicle_neighbours(nx, ny)
        ]

    def _can_vehicle_move(self, current, target):
        tx, ty = target

        if not self.is_road(tx, ty):
            return False

        return self._road_accepts_entry(current, target)

    def _road_accepts_entry(self, current, target):
        cx, cy = current
        tx, ty = target
        tile = self.map[tx, ty]

        if tile not in VEHICLE_DIRECTIONS:
            return True

        dx, dy = VEHICLE_DIRECTIONS[tile]

        return (tx - cx, ty - cy) == (dx, dy)

    def get_movement_axis(self, current, target):
        cx, cy = current
        tx, ty = target

        if abs(tx - cx) >= abs(ty - cy):
            return "horizontal"

        return "vertical"

    def clear_density(self):
        self.density[:, :] = 0

    def add_density(self, x, y):
        if self.in_bounds(x, y):
            self.density[x, y] += 1

    def get_density(self, x, y):
        if not self.in_bounds(x, y):
            return MAX_DENSITY

        return self.density[x, y]

    def clear_traffic_state(self):
        self.density[:, :] = 0
        self.vehicle_occupancy.clear()
        self.vehicle_reservations.clear()
        self.pedestrian_occupancy.clear()

    def register_vehicle(self, vehicle):
        current_tile = vehicle.get_current_tile()

        if self.is_road(*current_tile):
            self.vehicle_occupancy.setdefault(current_tile, vehicle)
            self.add_density(*current_tile)

        for tile in vehicle.get_reserved_tiles():
            if self.is_road(*tile):
                self.vehicle_reservations.setdefault(tile, vehicle)

    def register_pedestrian(self, pedestrian):
        tile = pedestrian.get_current_tile()

        if self.is_crossing_tile(*tile):
            self.pedestrian_occupancy.setdefault(tile, []).append(pedestrian)

    def reserve_vehicle_tile(self, tile, vehicle):
        if not self.is_road(*tile):
            return False

        occupant = self.vehicle_occupancy.get(tile)
        reservation = self.vehicle_reservations.get(tile)

        if occupant is not None and occupant is not vehicle:
            return False

        if reservation is not None and reservation is not vehicle:
            return False

        self.vehicle_reservations[tile] = vehicle

        return True

    def get_vehicle_at(self, x, y):
        return self.vehicle_occupancy.get((x, y))

    def get_blocking_vehicle(self, tile, vehicle=None):
        occupant = self.vehicle_occupancy.get(tile)

        if occupant is not None and occupant is not vehicle:
            return occupant

        reservation = self.vehicle_reservations.get(tile)

        if reservation is not None and reservation is not vehicle:
            return reservation

        return None

    def is_vehicle_tile_available(self, tile, vehicle=None):
        if not self.is_road(*tile):
            return False

        return self.get_blocking_vehicle(tile, vehicle) is None

    def has_pedestrian_on_crossing(self, tile):
        return bool(self.pedestrian_occupancy.get(tile))

    def get_flow_factor(self):
        if not self.roads:
            return 1.0

        total = sum(self.density[x, y] for x, y in self.roads)
        average = total / len(self.roads)
        peak = max(self.density[x, y] for x, y in self.roads)
        flow = 1.0 / (1.0 + average * 0.18 + peak * 0.06)

        return max(MIN_TRAFFIC_FLOW_FACTOR, min(1.0, flow))

    def _passable_tiles(self, profile):
        if profile == "vehicle":
            return self.roads

        return self.walkable_tiles

    def _is_passable(self, x, y, profile):
        if profile == "vehicle":
            return self.is_road(x, y)

        return self.is_walkable(x, y)

    def _find_access_points(self, zone_symbol, profile):
        zone_tiles = self._find_tiles(zone_symbol)
        passable_tiles = self._passable_tiles(profile)
        access = set()

        for zx, zy in zone_tiles:
            direct_access = [
                (nx, ny)
                for nx, ny in self._neighbours4(zx, zy)
                if self._is_passable(nx, ny, profile)
            ]

            if direct_access:
                access.update(direct_access)
                continue

            nearest_distance = None
            nearest_tiles = []

            for px, py in passable_tiles:
                distance = abs(px - zx) + abs(py - zy)

                if nearest_distance is None or distance < nearest_distance:
                    nearest_distance = distance
                    nearest_tiles = [(px, py)]
                elif distance == nearest_distance:
                    nearest_tiles.append((px, py))

            access.update(nearest_tiles)

        return sorted(access)

    def get_access_points(self, zone_symbol, profile):
        if profile == "vehicle":
            return self.vehicle_access.get(zone_symbol, [])

        return self.pedestrian_access.get(zone_symbol, [])

    def choose_access(self, zone_symbols, profile):
        pool = []

        for zone_symbol in zone_symbols:
            pool.extend(self.get_access_points(zone_symbol, profile))

        pool = sorted(set(pool))

        if not pool:
            pool = self._passable_tiles(profile)

        if not pool:
            return None

        return random.choice(pool)

    def choose_exit(self, profile):
        exits = [position for position in self.exits if self._is_passable(*position, profile)]

        if exits:
            return random.choice(exits)

        return self.choose_access(ZONE_SYMBOLS, profile)

    def is_reachable(self, start, target, profile):
        if start is None or target is None:
            return False

        sx, sy = start

        if not self._is_passable(sx, sy, profile):
            return False

        dist = self.get_distance_map(target, profile)

        return dist[sx, sy] < 9999

    def _choose_reachable_from(self, start, positions, profile, excluded=None):
        excluded = set(excluded or [])

        reachable = [
            position
            for position in sorted(set(positions))
            if position not in excluded
            and self._is_passable(*position, profile)
            and self.is_reachable(start, position, profile)
        ]

        if not reachable:
            return None

        return random.choice(reachable)

    def choose_reachable_access(self, start, zone_symbols, profile, excluded=None):
        pool = []

        for zone_symbol in zone_symbols:
            pool.extend(self.get_access_points(zone_symbol, profile))

        return self._choose_reachable_from(start, pool, profile, excluded)

    def choose_reachable_exit(self, start, profile, excluded=None):
        target = self._choose_reachable_from(start, self.exits, profile, excluded)

        if target is not None:
            return target

        return self.choose_reachable_road(start, excluded)

    def choose_reachable_road(self, start, excluded=None):
        return self._choose_reachable_from(start, self.roads, "vehicle", excluded)

    def choose_spawn(self, profile, zone_symbols=None):
        if profile == "vehicle":
            if not self.spawns:
                return None

            return random.choice(self.spawns)

        pool = []

        if zone_symbols:
            for zone_symbol in zone_symbols:
                pool.extend(self.get_access_points(zone_symbol, "pedestrian"))

        pool.extend(self.pedestrian_crossings)

        pool = [
            position
            for position in sorted(set(pool))
            if self.is_pedestrian_spawn_tile(*position)
        ]

        if not pool:
            pool = self.walkable_tiles

        if not pool:
            return None

        return random.choice(pool)

    def _target_seeds(self, target, profile):
        tx, ty = target

        if self._is_passable(tx, ty, profile):
            return [target]

        direct_access = [
            (nx, ny)
            for nx, ny in self._neighbours4(tx, ty)
            if self._is_passable(nx, ny, profile)
        ]

        if direct_access:
            return direct_access

        passable_tiles = self._passable_tiles(profile)

        if not passable_tiles:
            return []

        nearest_distance = min(
            abs(px - tx) + abs(py - ty)
            for px, py in passable_tiles
        )

        return [
            (px, py)
            for px, py in passable_tiles
            if abs(px - tx) + abs(py - ty) == nearest_distance
        ]

    def get_distance_map(self, target, profile="vehicle"):
        key = (profile, target)

        if key not in self.distance_cache:
            self.distance_cache[key] = self._compute_distance_map(target, profile)

        return self.distance_cache[key]

    def _compute_distance_map(self, target, profile):
        dist = np.full((self.mapW, self.mapH), 9999, dtype=np.int32)
        queue = deque()

        for sx, sy in self._target_seeds(target, profile):
            if not self._is_passable(sx, sy, profile):
                continue

            dist[sx, sy] = 0
            queue.append((sx, sy))

        while queue:
            x, y = queue.popleft()
            next_distance = dist[x, y] + 1

            if profile == "vehicle":
                neighbours = self.get_vehicle_predecessors(x, y)
            else:
                neighbours = self.get_neighbours(x, y, profile)

            for nx, ny in neighbours:
                if next_distance < dist[nx, ny]:
                    dist[nx, ny] = next_distance
                    queue.append((nx, ny))

        return dist

    def set_traffic_lights(self, traffic_lights):
        self.traffic_light_objects = traffic_lights

    def _nearby_lights(self, x, y, radius=3):
        lights = []

        for light in self.traffic_light_objects:
            lx, ly = light.position
            distance = abs(lx - x) + abs(ly - y)

            if distance <= radius:
                lights.append((distance, light))

        lights.sort(key=lambda item: item[0])

        return [light for _, light in lights]

    def _light_for_move(self, current, target):
        cx, cy = current
        tx, ty = target
        lights = self._nearby_lights(tx, ty) + self._nearby_lights(cx, cy)

        if not lights:
            return None

        return lights[0]

    def _vehicle_stop_tile(self, x, y):
        if not self.in_bounds(x, y):
            return False

        tile = self.map[x, y]

        return tile in (TRAFFIC_LIGHT, CROSSROAD) or (
            self.is_road(x, y) and bool(self._nearby_lights(x, y, radius=1))
        )

    def _vehicle_inside_controlled_tile(self, x, y):
        if not self.in_bounds(x, y):
            return False

        return self.map[x, y] in (TRAFFIC_LIGHT, CROSSROAD)

    def _tile_after_move(self, current, target):
        cx, cy = current
        tx, ty = target
        dx = tx - cx
        dy = ty - cy

        after = (tx + dx, ty + dy)

        if not self.in_bounds(*after):
            return None

        if not self.is_road(*after):
            return None

        return after

    def _move_direction(self, current, target):
        cx, cy = current
        tx, ty = target

        return tx - cx, ty - cy

    def _next_light_on_move(self, current, target):
        dx, dy = self._move_direction(current, target)

        if dx == 0 and dy == 0:
            return None

        tx, ty = target

        if self.in_bounds(tx, ty) and self.map[tx, ty] == TRAFFIC_LIGHT:
            return target

        nx = tx + dx
        ny = ty + dy

        if self.in_bounds(nx, ny) and self.map[nx, ny] == TRAFFIC_LIGHT:
            return nx, ny

        return None

    def vehicle_waits_for_queue_after_green_light(self, current, target, vehicle=None):
        tx, ty = target

        if not self.in_bounds(tx, ty):
            return False

        light_tile = self._next_light_on_move(current, target)

        if light_tile is None:
            return False

        light = self._light_for_move(current, light_tile)
        axis = self.get_movement_axis(current, target)

        if light is None or not light.is_vehicle_green_for_axis(axis):
            return False

        dx, dy = self._move_direction(current, target)
        after = (light_tile[0] + dx, light_tile[1] + dy)

        if not self.in_bounds(*after) or not self.is_road(*after):
            return False

        return self.get_blocking_vehicle(after, vehicle) is not None

    def vehicle_can_enter(self, current, target, vehicle=None):
        if not self.is_vehicle_tile_available(target, vehicle):
            return False

        if self.is_crossing_tile(*target) and self.has_pedestrian_on_crossing(target):
            return False

        if self._vehicle_inside_controlled_tile(*current):
            return True

        if not self._vehicle_stop_tile(*target):
            return True

        light = self._light_for_move(current, target)
        axis = self.get_movement_axis(current, target)

        return light is None or light.is_vehicle_green_for_axis(axis)

    def _pedestrian_inside_controlled_tile(self, x, y):
        if not self.in_bounds(x, y):
            return False

        return self.is_crossing_tile(x, y) and self.map[x, y] != PEDESTRIAN_WAY

    def pedestrian_can_enter(self, current, target):
        if self.is_road(*target) and self.get_blocking_vehicle(target) is not None:
            return False

        if self._pedestrian_inside_controlled_tile(*current):
            return True

        if not self.is_crossing_tile(*target):
            return True

        if self.map[target[0], target[1]] == PEDESTRIAN_WAY and not self.is_road(*target):
            return True

        light = self._light_for_move(current, target)
        crossing_axis = self.get_crossing_axis(*target)

        return light is None or light.is_pedestrian_green_for_axis(crossing_axis)
