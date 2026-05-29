# pedestrian.py

import math

from settings import *
from colors import PEDESTRIAN_COLOR


class Pedestrian:
    def __init__(self, game, spawn, missions):
        self.game = game

        sx, sy = spawn
        self.x = sx + 0.5
        self.y = sy + 0.5

        if isinstance(missions, tuple):
            missions = [missions]

        self.missions = list(missions)
        self.target = self.missions[0] if self.missions else spawn

        self.speed = PEDESTRIAN_SPEED
        self.state = STATE_WALK
        self.dir = (0, 1)
        self.finished = False

    def set_missions(self, missions):
        self.missions = list(missions)

        if self.missions:
            self.target = self.missions[0]
            self.finished = False
            self.state = STATE_WALK

    def update(self, dt):
        if self.finished:
            return

        if self.has_reached_target():
            self._advance_mission()

            if self.finished:
                return

        ix = int(self.x)
        iy = int(self.y)

        valid_neighbours = self.game.get_neighbours(ix, iy, "pedestrian")

        if not valid_neighbours:
            self.state = STATE_WAIT_LIGHT
            return

        dist = self.game.get_distance_map(self.target, "pedestrian")

        best_distance = min(dist[nx, ny] for nx, ny in valid_neighbours)

        if best_distance >= 9999:
            self.state = STATE_WAIT_LIGHT
            return

        nx, ny = min(
            valid_neighbours,
            key=lambda p: dist[p[0], p[1]]
        )

        if not self.game.pedestrian_can_enter((ix, iy), (nx, ny)):
            self.state = STATE_WAIT_LIGHT
            return

        if self.game.is_crossing_tile(nx, ny):
            self.state = STATE_CROSS
        else:
            self.state = STATE_WALK

        self._move_towards(nx, ny, dt)

    def _move_towards(self, nx, ny, dt):
        tx = nx + 0.5
        ty = ny + 0.5

        dx = tx - self.x
        dy = ty - self.y
        distance = math.hypot(dx, dy)

        if distance <= 0.001:
            return

        dx /= distance
        dy /= distance

        step = min(self.speed * dt, distance)

        self.dir = (dx, dy)
        self.x += dx * step
        self.y += dy * step

    def _advance_mission(self):
        if self.missions:
            self.missions.pop(0)

        if not self.missions:
            self.finished = True
            self.state = STATE_PEDESTRIAN_EXIT
            return

        self.target = self.missions[0]
        self.state = STATE_WALK

    def has_reached_target(self):
        tx, ty = self.target

        return int(self.x) == tx and int(self.y) == ty

    def is_finished(self):
        return self.finished

    def get_current_tile(self):
        return int(self.x), int(self.y)

    def draw(self, renderer):
        renderer.draw_circle(
            self.x,
            self.y,
            0.12,
            PEDESTRIAN_COLOR
        )
