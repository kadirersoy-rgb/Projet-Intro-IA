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
        if self.is_vehicle_green_for_axis(crossing_axis):
            return "GREEN"

        return "RED"

    def is_pedestrian_green_for_axis(self, crossing_axis):
        return self.get_pedestrian_state(crossing_axis) == "GREEN"

    def draw(self, renderer):
        x, y = self.position

        horizontal_color = TRAFFIC_LIGHT_COLORS[
            self.get_vehicle_state(HORIZONTAL)
        ]
        vertical_color = TRAFFIC_LIGHT_COLORS[
            self.get_vehicle_state(VERTICAL)
        ]
        crossing_axis = renderer.game.get_crossing_axis(x, y)
        pedestrian_color = TRAFFIC_LIGHT_COLORS[
            self.get_pedestrian_state(crossing_axis)
        ]

        renderer.draw_signal_box(x + 0.28, y + 0.36, horizontal_color)
        renderer.draw_signal_box(x + 0.72, y + 0.36, vertical_color)
        renderer.draw_signal_box(x + 0.50, y + 0.78, pedestrian_color, True)
