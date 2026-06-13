# traffic_light.py

from settings import *
from colors import TRAFFIC_LIGHT_COLORS


HORIZONTAL = "horizontal"
VERTICAL = "vertical"


class TrafficLight:
    def __init__(self, position):
        self.position = position
        self.phase = "H_GREEN"
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt

        if self.phase == "H_GREEN" and self.timer >= GREEN_LIGHT_DURATION:
            self.phase = "H_ORANGE"
            self.timer = 0.0

        elif self.phase == "H_ORANGE" and self.timer >= ORANGE_LIGHT_DURATION:
            self.phase = "V_GREEN"
            self.timer = 0.0

        elif self.phase == "V_GREEN" and self.timer >= GREEN_LIGHT_DURATION:
            self.phase = "V_ORANGE"
            self.timer = 0.0

        elif self.phase == "V_ORANGE" and self.timer >= ORANGE_LIGHT_DURATION:
            self.phase = "H_GREEN"
            self.timer = 0.0

    def get_vehicle_state(self, axis):
        if axis == HORIZONTAL:
            if self.phase == "H_GREEN":
                return "GREEN"

            if self.phase == "H_ORANGE":
                return "ORANGE"

            return "RED"

        if self.phase == "V_GREEN":
            return "GREEN"

        if self.phase == "V_ORANGE":
            return "ORANGE"

        return "RED"

    def is_vehicle_green_for_axis(self, axis):
        return self.get_vehicle_state(axis) == "GREEN"

    def get_pedestrian_state(self, crossing_axis):
        if self.get_vehicle_state(crossing_axis) == "RED":
            return "GREEN"

        return "RED"

    def is_pedestrian_green_for_axis(self, crossing_axis):
        return self.get_pedestrian_state(crossing_axis) == "GREEN"

    def get_vehicle_axis(self, renderer):
        x, y = self.position

        horizontal_score = 0
        vertical_score = 0

        for nx, ny in ((x - 1, y), (x + 1, y)):
            if renderer.game.is_road(nx, ny):
                horizontal_score += 1

        for nx, ny in ((x, y - 1), (x, y + 1)):
            if renderer.game.is_road(nx, ny):
                vertical_score += 1

        if vertical_score > horizontal_score:
            return VERTICAL

        return HORIZONTAL

    def get_crossroad_direction(self, renderer):
        crossroad = self.get_crossroad_position(renderer)

        if crossroad is None:
            return 0, 0

        x, y = self.position
        cx, cy = crossroad

        return cx - x, cy - y

    def get_crossroad_position(self, renderer):
        x, y = self.position

        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx = x + dx
            ny = y + dy

            if (
                renderer.game.in_bounds(nx, ny)
                and renderer.game.map[nx, ny] == CROSSROAD
            ):
                return nx, ny

        return None

    def intersection_has_pedestrian_crossing(self, renderer, crossroad):
        x, y = crossroad

        return any(
            renderer.game.in_bounds(nx, ny)
            and renderer.game.is_crossing_tile(nx, ny)
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
        )

    def is_pedestrian_signal_owner(self, renderer, crossroad):
        x, y = crossroad
        traffic_lights = [
            (nx, ny)
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
            if (
                renderer.game.in_bounds(nx, ny)
                and renderer.game.map[nx, ny] == TRAFFIC_LIGHT
            )
        ]

        return traffic_lights and self.position == sorted(traffic_lights)[0]

    def get_pedestrian_signal_position(self, renderer):
        x, y = self.position
        dx, dy = self.get_crossroad_direction(renderer)

        if dy != 0:
            side_x = -1 if dy < 0 else 1
            return x + 0.5 + side_x * 0.64, y + 0.5

        if dx != 0:
            side_y = -1 if dx > 0 else 1
            return x + 0.5, y + 0.5 + side_y * 0.64

        return x + 0.5, y + 0.5

    def draw_pedestrian_corner_signals(self, renderer, crossroad, color):
        x, y = crossroad
        offset = 0.18

        positions = [
            (x + offset, y + offset),
            (x + 1 - offset, y + offset),
            (x + offset, y + 1 - offset),
            (x + 1 - offset, y + 1 - offset),
        ]

        for px, py in positions:
            renderer.draw_pedestrian_signal_box(px, py, color)

    def get_crosswalk_before_light(self, renderer):
        crossroad = self.get_crossroad_position(renderer)

        if crossroad is None:
            return None

        x, y = self.position
        cx, cy = crossroad
        dx = cx - x
        dy = cy - y
        px = x - dx
        py = y - dy

        if (
            renderer.game.in_bounds(px, py)
            and renderer.game.map[px, py] == PEDESTRIAN_WAY
        ):
            return px, py

        return None

    def draw_pedestrian_crosswalk_signals(self, renderer, crosswalk, color):
        x, y = crosswalk
        axis = renderer.game.get_crossing_axis(x, y)

        if axis == HORIZONTAL:
            positions = [
                (x + 0.5, y + 0.12),
                (x + 0.5, y + 0.88),
            ]
        else:
            positions = [
                (x + 0.12, y + 0.5),
                (x + 0.88, y + 0.5),
            ]

        for px, py in positions:
            renderer.draw_pedestrian_signal_box(px, py, color)

    def draw(self, renderer):
        x, y = self.position
        vehicle_axis = self.get_vehicle_axis(renderer)
        vehicle_color = TRAFFIC_LIGHT_COLORS[
            self.get_vehicle_state(vehicle_axis)
        ]

        crosswalk = self.get_crosswalk_before_light(renderer)
        crossing_axis = (
            renderer.game.get_crossing_axis(*crosswalk)
            if crosswalk is not None
            else vehicle_axis
        )
        pedestrian_color = TRAFFIC_LIGHT_COLORS[
            self.get_pedestrian_state(crossing_axis)
        ]

        renderer.draw_vehicle_signal_box(x, y, vehicle_color, vehicle_axis)

        if crosswalk is not None:
            self.draw_pedestrian_crosswalk_signals(
                renderer,
                crosswalk,
                pedestrian_color
            )
