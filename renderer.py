# renderer.py

import pygame

from settings import *
from colors import *


class Renderer:
    def __init__(self, game):
        self.game = game

        self.map_pixel_width = game.mapW * ZOOM
        self.map_pixel_height = game.mapH * ZOOM
        self.SCREEN_WIDTH = max(
            self.map_pixel_width + LEGEND_PANEL_WIDTH,
            MIN_WINDOW_WIDTH
        )
        self.SCREEN_HEIGHT = max(self.map_pixel_height, MIN_WINDOW_HEIGHT)
        self.legend_x = self.SCREEN_WIDTH - LEGEND_PANEL_WIDTH
        self.map_offset_x = (self.legend_x - self.map_pixel_width) // 2

        pygame.display.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )

        pygame.display.set_caption("Traffic Simulator")
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 16)

    def grid_to_cell(self, x, y):
        sx = self.map_offset_x + x * ZOOM
        sy = self.map_pixel_height - (y + 1) * ZOOM

        return sx, sy

    def grid_to_point(self, x, y):
        sx = self.map_offset_x + x * ZOOM
        sy = self.map_pixel_height - y * ZOOM

        return sx, sy

    def cell_rect(self, x, y, inset=0):
        sx, sy = self.grid_to_cell(x, y)

        return pygame.Rect(
            sx + inset,
            sy + inset,
            ZOOM - inset * 2,
            ZOOM - inset * 2
        )

    def draw_rect(self, x, y, w, h, color, width=0):
        sx, sy = self.grid_to_cell(x, y)

        pygame.draw.rect(
            self.screen,
            color,
            (
                sx,
                sy - (h - 1) * ZOOM,
                w * ZOOM,
                h * ZOOM
            ),
            width
        )

    def draw_circle(self, x, y, radius, color):
        sx, sy = self.grid_to_point(x, y)

        pygame.draw.circle(
            self.screen,
            color,
            (int(sx), int(sy)),
            int(radius * ZOOM)
        )

    def draw_triangle(self, a, b, c, color):
        p1 = self.grid_to_point(a[0], a[1])
        p2 = self.grid_to_point(b[0], b[1])
        p3 = self.grid_to_point(c[0], c[1])

        pygame.draw.polygon(
            self.screen,
            color,
            [
                (int(p1[0]), int(p1[1])),
                (int(p2[0]), int(p2[1])),
                (int(p3[0]), int(p3[1]))
            ]
        )

    def draw_polygon(self, points, color, width=0):
        screen_points = []

        for x, y in points:
            sx, sy = self.grid_to_point(x, y)
            screen_points.append((int(sx), int(sy)))

        pygame.draw.polygon(self.screen, color, screen_points, width)

    def draw_text(self, x, y, text, color=Color.white, big=False):
        font = self.font_big if big else self.font_small
        surface = font.render(str(text), True, color)
        self.screen.blit(surface, (x, y))

    def _edge_arrow_direction(self, x, y):
        if x == 0:
            return "right"

        if x == self.game.mapW - 1:
            return "left"

        if y == 0:
            return "up"

        if y == self.game.mapH - 1:
            return "down"

        return "right"

    def draw_arrow_icon(self, rect, color, direction):
        icon = rect.inflate(-max(2, rect.width // 8), -max(2, rect.height // 8))
        radius = max(3, icon.width // 8)

        pygame.draw.rect(self.screen, color, icon, border_radius=radius)
        pygame.draw.rect(
            self.screen,
            self._mix(color, Color.white, 0.28),
            icon,
            max(1, icon.width // 20),
            border_radius=radius
        )

        vectors = {
            "right": (1, 0),
            "left": (-1, 0),
            "up": (0, -1),
            "down": (0, 1),
        }
        dx, dy = vectors[direction]
        px, py = -dy, dx

        cx, cy = icon.center
        size = min(icon.width, icon.height)
        tip = (
            cx + dx * size * 0.34,
            cy + dy * size * 0.34
        )
        base = (
            cx + dx * size * 0.04,
            cy + dy * size * 0.04
        )
        tail = (
            cx - dx * size * 0.28,
            cy - dy * size * 0.28
        )

        pygame.draw.line(
            self.screen,
            Color.white,
            (int(tail[0]), int(tail[1])),
            (int(base[0]), int(base[1])),
            max(3, int(size * 0.16))
        )

        head = [
            tip,
            (
                base[0] + px * size * 0.22,
                base[1] + py * size * 0.22
            ),
            (
                base[0] - px * size * 0.22,
                base[1] - py * size * 0.22
            )
        ]
        pygame.draw.polygon(self.screen, Color.white, head)

    def draw_access_arrow_tile(self, x, y, tile):
        rect = self.cell_rect(x, y)
        color = CITY_COLORS[SPAWN] if tile == SPAWN else CITY_COLORS[EXIT]
        direction = self._edge_arrow_direction(x, y)

        if tile == EXIT:
            direction = {
                "right": "left",
                "left": "right",
                "up": "down",
                "down": "up",
            }[direction]

        self.draw_arrow_icon(rect, color, direction)

    def draw_vehicle(self, vehicle):
        vehicle.draw(self)

    def draw_pedestrian(self, pedestrian):
        pedestrian.draw(self)

    def _mix(self, a, b, t):
        return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))

    def _traffic_color(self, x, y):
        nb = self.game.density[x, y]
        index = min(nb, len(traffic_colors) - 1)

        return traffic_colors[index]

    def draw_road_tile(self, x, y):
        tile = self.game.map[x, y]
        rect = self.cell_rect(x, y)
        asphalt = (48, 50, 53)
        density_color = self._traffic_color(x, y)
        road_color = self._mix(asphalt, density_color, 0.35)

        pygame.draw.rect(self.screen, road_color, rect)

        edge_color = (34, 35, 37)
        pygame.draw.rect(self.screen, edge_color, rect, max(1, ZOOM // 18))

        cx = rect.centerx
        cy = rect.centery
        mark_color = (215, 215, 200)
        mark_width = max(1, ZOOM // 14)

        if tile in (ROAD_RIGHT, ROAD_LEFT, SPAWN, EXIT):
            pygame.draw.line(
                self.screen,
                mark_color,
                (rect.left + ZOOM * 0.25, cy),
                (rect.right - ZOOM * 0.25, cy),
                mark_width
            )

        elif tile in (ROAD_UP, ROAD_DOWN):
            pygame.draw.line(
                self.screen,
                mark_color,
                (cx, rect.top + ZOOM * 0.25),
                (cx, rect.bottom - ZOOM * 0.25),
                mark_width
            )

        elif tile == CROSSROAD:
            pygame.draw.circle(
                self.screen,
                (72, 74, 76),
                rect.center,
                int(ZOOM * 0.34)
            )

        if self.game.is_crossing_tile(x, y):
            self.draw_crosswalk_tile(x, y)

        if tile in (SPAWN, EXIT):
            self.draw_access_arrow_tile(x, y, tile)

    def draw_crosswalk_tile(self, x, y):
        rect = self.cell_rect(x, y, max(1, ZOOM // 18))
        stripe_color = (245, 245, 235)
        stripe_count = 3
        stripe_width = max(2, rect.width // 7)
        axis = self.game.get_crossing_axis(x, y)

        if axis == "horizontal":
            gap = rect.width // stripe_count

            for i in range(stripe_count):
                sx = rect.left + i * gap + gap // 3
                stripe = pygame.Rect(
                    sx,
                    rect.top + ZOOM * 0.12,
                    stripe_width,
                    rect.height - ZOOM * 0.24
                )
                pygame.draw.rect(self.screen, stripe_color, stripe)

        else:
            gap = rect.height // stripe_count

            for i in range(stripe_count):
                sy = rect.top + i * gap + gap // 3
                stripe = pygame.Rect(
                    rect.left + ZOOM * 0.12,
                    sy,
                    rect.width - ZOOM * 0.24,
                    stripe_width
                )
                pygame.draw.rect(self.screen, stripe_color, stripe)

    def draw_sidewalk_tile(self, x, y, color):
        rect = self.cell_rect(x, y)
        tile = self.game.map[x, y]

        if tile in ("H", "W", "C"):
            pygame.draw.rect(self.screen, color, rect.inflate(-2, -2))
            pygame.draw.rect(
                self.screen,
                self._mix(color, Color.black, 0.35),
                rect.inflate(-2, -2),
                max(1, ZOOM // 18)
            )

            shine = pygame.Rect(
                int(rect.left + ZOOM * 0.18),
                int(rect.top + ZOOM * 0.16),
                max(2, int(ZOOM * 0.18)),
                max(2, int(ZOOM * 0.18))
            )
            pygame.draw.rect(self.screen, self._mix(color, Color.white, 0.18), shine)

        elif tile == BUILDING:
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(
                self.screen,
                (18, 19, 19),
                rect,
                max(1, ZOOM // 18)
            )

        else:
            pygame.draw.rect(self.screen, color, rect)
            line_color = self._mix(color, Color.black, 0.18)
            pygame.draw.line(
                self.screen,
                line_color,
                (rect.left, rect.centery),
                (rect.right, rect.centery),
                max(1, ZOOM // 24)
            )
            pygame.draw.line(
                self.screen,
                line_color,
                (rect.centerx, rect.top),
                (rect.centerx, rect.bottom),
                max(1, ZOOM // 24)
            )

        if self.game.map[x, y] == PEDESTRIAN_WAY:
            self.draw_crosswalk_tile(x, y)

    def draw_signal_box(self, x, y, color, pedestrian=False):
        sx, sy = self.grid_to_point(x, y)
        size = int(ZOOM * (0.34 if pedestrian else 0.42))
        rect = pygame.Rect(0, 0, size, size)
        rect.center = (int(sx), int(sy))

        pygame.draw.rect(
            self.screen,
            (18, 18, 18),
            rect,
            border_radius=max(2, ZOOM // 12)
        )
        pygame.draw.circle(
            self.screen,
            color,
            rect.center,
            max(3, size // 4)
        )
        pygame.draw.rect(
            self.screen,
            (2, 2, 2),
            rect,
            max(1, ZOOM // 24),
            border_radius=max(2, ZOOM // 12)
        )

    def _draw_vehicle_signal_pixels(self, rect, color, axis):
        pygame.draw.rect(
            self.screen,
            (12, 12, 12),
            rect,
            border_radius=max(2, rect.width // 5)
        )

        pygame.draw.rect(
            self.screen,
            (230, 230, 215),
            rect,
            max(1, rect.width // 12),
            border_radius=max(2, rect.width // 5)
        )

        pygame.draw.circle(
            self.screen,
            color,
            rect.center,
            max(3, min(rect.width, rect.height) // 4)
        )

        mark_color = (235, 235, 225)

        if axis == "horizontal":
            pygame.draw.line(
                self.screen,
                mark_color,
                (rect.left + 3, rect.bottom - 3),
                (rect.right - 3, rect.bottom - 3),
                max(1, rect.height // 10)
            )
        else:
            pygame.draw.line(
                self.screen,
                mark_color,
                (rect.right - 3, rect.top + 3),
                (rect.right - 3, rect.bottom - 3),
                max(1, rect.width // 10)
            )

    def draw_vehicle_signal_box(self, x, y, color, axis):
        cell = self.cell_rect(x, y)
        size = max(12, int(ZOOM * 0.68))
        rect = pygame.Rect(0, 0, size, size)
        rect.center = cell.center

        self._draw_vehicle_signal_pixels(rect, color, axis)

    def _draw_pedestrian_signal_pixels(self, rect, color):
        pygame.draw.rect(
            self.screen,
            (12, 12, 12),
            rect,
            border_radius=max(2, rect.width // 4)
        )

        pygame.draw.rect(
            self.screen,
            (190, 190, 178),
            rect,
            max(1, rect.width // 8),
            border_radius=max(2, rect.width // 4)
        )

        cx = rect.centerx
        head_y = rect.top + rect.height * 0.28
        body_top = rect.top + rect.height * 0.42
        body_bottom = rect.top + rect.height * 0.66
        foot_y = rect.bottom - rect.height * 0.16

        pygame.draw.circle(
            self.screen,
            color,
            (int(cx), int(head_y)),
            max(2, rect.width // 5)
        )

        pygame.draw.line(
            self.screen,
            color,
            (int(cx), int(body_top)),
            (int(cx), int(body_bottom)),
            max(2, rect.width // 6)
        )

        if color == TRAFFIC_LIGHT_COLORS["GREEN"]:
            pygame.draw.line(
                self.screen,
                color,
                (int(cx), int(body_bottom)),
                (int(rect.left + rect.width * 0.28), int(foot_y)),
                max(2, rect.width // 7)
            )
            pygame.draw.line(
                self.screen,
                color,
                (int(cx), int(body_bottom)),
                (int(rect.right - rect.width * 0.22), int(foot_y)),
                max(2, rect.width // 7)
            )
            pygame.draw.line(
                self.screen,
                color,
                (int(cx), int(body_top)),
                (int(rect.right - rect.width * 0.20), int(body_top + rect.height * 0.12)),
                max(2, rect.width // 8)
            )
        else:
            pygame.draw.line(
                self.screen,
                color,
                (int(cx), int(body_bottom)),
                (int(cx - rect.width * 0.18), int(foot_y)),
                max(2, rect.width // 7)
            )
            pygame.draw.line(
                self.screen,
                color,
                (int(cx), int(body_bottom)),
                (int(cx + rect.width * 0.18), int(foot_y)),
                max(2, rect.width // 7)
            )
            pygame.draw.line(
                self.screen,
                color,
                (int(rect.left + rect.width * 0.26), int(body_top + rect.height * 0.05)),
                (int(rect.right - rect.width * 0.26), int(body_top + rect.height * 0.05)),
                max(2, rect.width // 8)
            )

    def draw_pedestrian_signal_box(self, x, y, color):
        sx, sy = self.grid_to_point(x, y)
        rect = pygame.Rect(
            0,
            0,
            max(8, int(ZOOM * 0.38)),
            max(12, int(ZOOM * 0.60))
        )
        rect.center = (int(sx), int(sy))

        pole_bottom = rect.bottom + max(3, ZOOM // 5)
        pygame.draw.line(
            self.screen,
            (25, 25, 25),
            rect.midbottom,
            (rect.centerx, pole_bottom),
            max(2, ZOOM // 10)
        )

        self._draw_pedestrian_signal_pixels(rect, color)

    def draw_legend_sample(self, rect, kind, color):
        if kind == "entry":
            self.draw_arrow_icon(rect, CITY_COLORS[SPAWN], "right")
            return

        if kind == "exit":
            self.draw_arrow_icon(rect, CITY_COLORS[EXIT], "left")
            return

        if kind == "vehicle_light":
            self._draw_vehicle_signal_pixels(
                rect.inflate(-6, -6),
                TRAFFIC_LIGHT_COLORS["GREEN"],
                "horizontal"
            )
            return

        if kind == "pedestrian_light":
            self._draw_pedestrian_signal_pixels(
                rect.inflate(-8, -4),
                TRAFFIC_LIGHT_COLORS["GREEN"]
            )
            return

        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (18, 18, 18), rect, 1)

        if kind == "road":
            pygame.draw.line(
                self.screen,
                (230, 230, 215),
                (rect.left + 5, rect.centery),
                (rect.right - 5, rect.centery),
                2
            )

        elif kind == "crosswalk":
            for i in range(3):
                stripe = pygame.Rect(
                    rect.left + 5 + i * 7,
                    rect.top + 4,
                    3,
                    rect.height - 8
                )
                pygame.draw.rect(self.screen, Color.white, stripe)

        elif kind == "building":
            inner = rect.inflate(-5, -5)
            pygame.draw.rect(self.screen, color, inner)
            pygame.draw.rect(
                self.screen,
                self._mix(color, Color.black, 0.35),
                inner,
                2
            )

    def draw_legend_item(self, x, y, label, kind, color):
        sample = pygame.Rect(x, y, 30, 30)
        self.draw_legend_sample(sample, kind, color)
        self.draw_text(x + 38, y + 5, label, (235, 235, 225))

    def draw_legend(self):
        left = self.legend_x
        pygame.draw.rect(
            self.screen,
            (20, 21, 21),
            (left, 0, LEGEND_PANEL_WIDTH, self.SCREEN_HEIGHT)
        )
        pygame.draw.line(
            self.screen,
            (55, 55, 50),
            (left, 0),
            (left, self.SCREEN_HEIGHT),
            2
        )

        self.draw_text(left + 22, 22, "Legende", Color.white, True)

        items = [
            ("Entree vehicules", "entry", CITY_COLORS[SPAWN]),
            ("Sortie vehicules", "exit", CITY_COLORS[EXIT]),
            ("Habitations", "building", CITY_COLORS["H"]),
            ("Centre-ville", "building", CITY_COLORS["C"]),
            ("Bureaux / travail", "building", CITY_COLORS["W"]),
            ("Route", "road", CITY_COLORS[ROAD_RIGHT]),
            ("Trottoir", "sidewalk", CITY_COLORS[EMPTY]),
            ("Passage pieton", "crosswalk", CITY_COLORS[PEDESTRIAN_WAY]),
            ("Feu voiture", "vehicle_light", TRAFFIC_LIGHT_COLORS["GREEN"]),
            ("Feu pieton", "pedestrian_light", TRAFFIC_LIGHT_COLORS["GREEN"]),
        ]

        start_y = 78

        for index, (label, kind, color) in enumerate(items):
            x = left + 24
            y = start_y + index * 48

            self.draw_legend_item(x, y, label, kind, color)

    def draw_map(self):
        self.screen.fill(Color.black)

        for x in range(self.game.mapW):
            for y in range(self.game.mapH):
                tile = self.game.map[x, y]

                if self.game.is_road(x, y):
                    self.draw_road_tile(x, y)
                else:
                    color = CITY_COLORS.get(tile, Color.black)
                    self.draw_sidewalk_tile(x, y, color)

                if SHOW_GRID:
                    self.draw_rect(x, y, 1, 1, Color.black, 1)

        self.draw_legend()

    def draw_ui(self, current_period, nb_vehicles, nb_pedestrians):
        left = self.map_offset_x + 10

        self.draw_text(
            left,
            10,
            f"Periode : {current_period}",
            Color.white,
            True
        )

        self.draw_text(
            left,
            40,
            f"Voitures : {nb_vehicles}",
            Color.white
        )

        self.draw_text(
            left,
            60,
            f"Pietons : {nb_pedestrians}",
            Color.white
        )

    def draw(self, vehicles, pedestrians, traffic_lights, current_period):
        self.draw_map()

        for vehicle in vehicles:
            self.draw_vehicle(vehicle)

        for pedestrian in pedestrians:
            self.draw_pedestrian(pedestrian)

        for light in traffic_lights:
            light.draw(self)

        self.draw_ui(
            current_period,
            len(vehicles),
            len(pedestrians)
        )

        pygame.display.flip()
