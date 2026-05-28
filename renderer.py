# renderer.py

import pygame

from settings import *
from colors import *


class Renderer:
    def __init__(self, game):
        self.game = game

        self.SCREEN_WIDTH = game.mapW * ZOOM
        self.SCREEN_HEIGHT = (game.mapH + 1) * ZOOM

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
        sx = x * ZOOM
        sy = self.SCREEN_HEIGHT - (y + 1) * ZOOM

        return sx, sy

    def grid_to_point(self, x, y):
        sx = x * ZOOM
        sy = self.SCREEN_HEIGHT - y * ZOOM

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
        pygame.draw.rect(self.screen, color, rect)

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

    def draw_ui(self, current_period, nb_vehicles, nb_pedestrians):
        self.draw_text(
            10,
            10,
            f"Periode : {current_period}",
            Color.white,
            True
        )

        self.draw_text(
            10,
            40,
            f"Voitures : {nb_vehicles}",
            Color.white
        )

        self.draw_text(
            10,
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
