# vehicle.py

import math
import random
from settings import *
from colors import VEHICLE_COLOR, VEHICLE_COLORS


class Vehicle:
    def __init__(self, game, spawn, missions):
        self.game = game

        sx, sy = spawn
        self.x = sx + 0.5
        self.y = sy + 0.5

        if isinstance(missions, tuple):
            missions = [missions]

        self.missions = list(missions)
        self.targets = self.missions
        self.target = self.missions[0] if self.missions else spawn

        self.dir = (1, 0)
        self.next_tile = (int(self.x), int(self.y))
        self.previous_tile = None
        self.speed = VEHICLE_SPEED
        self.state = STATE_DRIVE
        self.finished = False
        self.orange_light_decisions = {}
        self.color = random.choice(VEHICLE_COLORS)

    def set_missions(self, missions):
        self.missions = list(missions)
        self.targets = self.missions

        if self.missions:
            self.target = self.missions[0]
            self.finished = False
            self.state = STATE_DRIVE
            self.next_tile = self.get_current_tile()
            self.previous_tile = None

    def update(self, dt):
        if self.finished:
            return

        if self.has_reached_target():
            self._advance_mission()

            if self.finished:
                return

        ix = int(self.x)
        iy = int(self.y)
        current_tile = (ix, iy)

        possible_neighbours = [
            (nx, ny)
            for nx, ny in self._movement_candidates(current_tile)
            if self.game.get_density(nx, ny) < MAX_DENSITY
        ]

        if not possible_neighbours:
            self._stop_in_current_tile(STATE_TRAFFIC_JAM)
            return

        dist = self.game.get_distance_map(self.target, "vehicle")

        best_distance = min(dist[nx, ny] for nx, ny in possible_neighbours)

        if best_distance >= 9999:
            self._stop_in_current_tile(STATE_TRAFFIC_JAM)
            return

        nx, ny = min(
            possible_neighbours,
            key=lambda p: (
                dist[p[0], p[1]]
                + self._turn_penalty(p)
            )
        )

        blocking_vehicle = self.game.get_blocking_vehicle((nx, ny), self)

        if blocking_vehicle is not None:
            if blocking_vehicle.is_stopped_by_traffic():
                self._stop_in_current_tile(STATE_TRAFFIC_JAM)
            else:
                self._follow_moving_vehicle(nx, ny, dt)

            return

        if self.game.vehicle_waits_for_queue_after_green_light(
            current_tile,
            (nx, ny),
            self
        ):
            self._stop_in_current_tile(STATE_FOLLOW)
            return

        if not self.game.vehicle_can_enter(current_tile, (nx, ny), self):
            self._stop_in_current_tile(STATE_RED_LIGHT)
            return

        if not self.game.reserve_vehicle_tile((nx, ny), self):
            blocking_vehicle = self.game.get_blocking_vehicle((nx, ny), self)

            if blocking_vehicle is not None and not blocking_vehicle.is_stopped_by_traffic():
                self._follow_moving_vehicle(nx, ny, dt)
            else:
                self._stop_in_current_tile(STATE_BRAKE)

            return

        self.next_tile = (nx, ny)
        self._move_towards(nx, ny, dt)

    def _movement_candidates(self, current_tile):
        ix, iy = current_tile
        neighbours = self.game.get_neighbours(ix, iy, "vehicle")
        tile = self.game.map[ix, iy]

        if tile in (CROSSROAD, TRAFFIC_LIGHT, SPAWN, EXIT):
            return neighbours

        dx, dy = self.dir

        if abs(dx) >= abs(dy):
            sign = 1 if dx >= 0 else -1
            same_lane = [
                (nx, ny)
                for nx, ny in neighbours
                if ny == iy and (nx - ix) * sign > 0
            ]
        else:
            sign = 1 if dy >= 0 else -1
            same_lane = [
                (nx, ny)
                for nx, ny in neighbours
                if nx == ix and (ny - iy) * sign > 0
            ]

        if same_lane:
            return same_lane

        return neighbours

    def _turn_penalty(self, target_tile):
        dx, dy = self.dir
        tx = target_tile[0] + 0.5 - self.x
        ty = target_tile[1] + 0.5 - self.y

        if abs(dx) < 0.001 and abs(dy) < 0.001:
            return 0

        dot = dx * tx + dy * ty

        if dot >= 0:
            return 0

        return VEHICLE_TURN_PENALTY

    def _stop_in_current_tile(self, state):
        ix, iy = self.get_current_tile()

        self.x = ix + 0.5
        self.y = iy + 0.5
        self.next_tile = (ix, iy)
        self.previous_tile = None
        self.state = state

    def _follow_moving_vehicle(self, nx, ny, dt):
        ix, iy = self.get_current_tile()
        target_x = nx + 0.5
        target_y = ny + 0.5

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        if distance <= 0.001:
            self.state = STATE_FOLLOW
            return

        dx /= distance
        dy /= distance

        center_x = ix + 0.5
        center_y = iy + 0.5
        safe_x = center_x + dx * VEHICLE_FOLLOW_OFFSET
        safe_y = center_y + dy * VEHICLE_FOLLOW_OFFSET
        distance_to_safe = math.hypot(safe_x - self.x, safe_y - self.y)

        if distance_to_safe > 0.001:
            step = min((self.speed * dt) * 0.5, distance_to_safe)
            move_x = (safe_x - self.x) / distance_to_safe
            move_y = (safe_y - self.y) / distance_to_safe

            self.x += move_x * step
            self.y += move_y * step

        self.dir = (dx, dy)
        self.next_tile = (ix, iy)
        self.previous_tile = None
        self.state = STATE_FOLLOW

    def _move_towards(self, nx, ny, dt):
        ix = int(self.x)
        iy = int(self.y)
        old_tile = (ix, iy)

        tx = nx + 0.5
        ty = ny + 0.5

        dx = tx - self.x
        dy = ty - self.y
        distance = math.hypot(dx, dy)

        if distance <= 0.001:
            return

        dx /= distance
        dy /= distance

        density = max(
            self.game.get_density(ix, iy),
            self.game.get_density(nx, ny)
        )
        slowdown = 1.0 + density * TRAFFIC_SLOWDOWN_FACTOR
        speed = self.speed / slowdown
        step = min(speed * dt, distance)

        self.dir = (dx, dy)
        self.x += dx * step
        self.y += dy * step

        new_tile = self.get_current_tile()

        if new_tile != old_tile:
            self.previous_tile = old_tile

        center_x = new_tile[0] + 0.5
        center_y = new_tile[1] + 0.5

        if math.hypot(self.x - center_x, self.y - center_y) < 0.18:
            self.previous_tile = None

        if density >= MAX_DENSITY - 1:
            self.state = STATE_TRAFFIC_JAM
        else:
            self.state = STATE_DRIVE

    def _advance_mission(self):
        if self.missions:
            self.missions.pop(0)

        if not self.missions:
            self.finished = True
            self.state = STATE_EXIT
            return

        self.target = self.missions[0]
        self.state = STATE_DRIVE

    def has_reached_target(self):
        tx, ty = self.target

        return int(self.x) == tx and int(self.y) == ty

    def is_finished(self):
        return self.finished

    def is_stopped_by_traffic(self):
        return self.state in (
            STATE_BRAKE,
            STATE_RED_LIGHT,
            STATE_TRAFFIC_JAM,
        )

    def stops_for_orange_light(self, light_position):
        if light_position not in self.orange_light_decisions:
            self.orange_light_decisions[light_position] = (
                random.random() < ORANGE_LIGHT_STOP_PROBABILITY
            )

        return self.orange_light_decisions[light_position]

    def reset_orange_light_decision(self, light_position):
        self.orange_light_decisions.pop(light_position, None)

    def get_current_tile(self):
        return int(self.x), int(self.y)

    def get_reserved_tiles(self):
        current = self.get_current_tile()
        reserved = [current]

        if self.next_tile != current:
            reserved.append(self.next_tile)

        if self.previous_tile is not None and self.previous_tile not in reserved:
            reserved.append(self.previous_tile)

        return reserved

    def get_density_tiles(self):
        return [self.get_current_tile()]

    def draw(self, renderer):
        x = self.x
        y = self.y
        dx, dy = self.dir

        norm = math.hypot(dx, dy)

        if norm < 0.001:
            renderer.draw_circle(x, y, 0.25, VEHICLE_COLOR)
            return

        dx /= norm
        dy /= norm

        lx, ly = -dy, dx

        length = 0.58
        width = 0.26

        front_left = (
            x + length * 0.50 * dx + width * 0.50 * lx,
            y + length * 0.50 * dy + width * 0.50 * ly
        )
        front_right = (
            x + length * 0.50 * dx - width * 0.50 * lx,
            y + length * 0.50 * dy - width * 0.50 * ly
        )
        rear_right = (
            x - length * 0.50 * dx - width * 0.50 * lx,
            y - length * 0.50 * dy - width * 0.50 * ly
        )
        rear_left = (
            x - length * 0.50 * dx + width * 0.50 * lx,
            y - length * 0.50 * dy + width * 0.50 * ly
        )

        body = [front_left, front_right, rear_right, rear_left]
        renderer.draw_polygon(body, (18, 18, 18))
        renderer.draw_polygon(body, self.color)
        renderer.draw_polygon(body, (18, 18, 18), 1)

        windshield = [
            (
                x + length * 0.22 * dx + width * 0.34 * lx,
                y + length * 0.22 * dy + width * 0.34 * ly
            ),
            (
                x + length * 0.22 * dx - width * 0.34 * lx,
                y + length * 0.22 * dy - width * 0.34 * ly
            ),
            (
                x + length * 0.02 * dx - width * 0.28 * lx,
                y + length * 0.02 * dy - width * 0.28 * ly
            ),
            (
                x + length * 0.02 * dx + width * 0.28 * lx,
                y + length * 0.02 * dy + width * 0.28 * ly
            ),
        ]
        renderer.draw_polygon(windshield, (80, 160, 210))

        headlight_left = (
            x + length * 0.54 * dx + width * 0.28 * lx,
            y + length * 0.54 * dy + width * 0.28 * ly
        )
        headlight_right = (
            x + length * 0.54 * dx - width * 0.28 * lx,
            y + length * 0.54 * dy - width * 0.28 * ly
        )
        rear_light_left = (
            x - length * 0.54 * dx + width * 0.30 * lx,
            y - length * 0.54 * dy + width * 0.30 * ly
        )
        rear_light_right = (
            x - length * 0.54 * dx - width * 0.30 * lx,
            y - length * 0.54 * dy - width * 0.30 * ly
        )

        renderer.draw_circle(*headlight_left, 0.035, (255, 246, 150))
        renderer.draw_circle(*headlight_right, 0.035, (255, 246, 150))
        renderer.draw_circle(*rear_light_left, 0.032, (220, 35, 35))
        renderer.draw_circle(*rear_light_right, 0.032, (220, 35, 35))
