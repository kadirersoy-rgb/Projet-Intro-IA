# utils.py

import math


# Clamp une valeur entre un minimum et un maximum
def clamp(value, minimum, maximum):

    return max(minimum, min(value, maximum))


# Distance euclidienne entre deux points
def distance(x1, y1, x2, y2):

    dx = x2 - x1
    dy = y2 - y1

    return math.hypot(dx, dy)


# Distance de Manhattan entre deux points
def manhattan_distance(x1, y1, x2, y2):

    return abs(x1 - x2) + abs(y1 - y2)


# Normalisation d'un vecteur
def normalize(dx, dy):

    norm = math.hypot(dx, dy)

    if norm == 0:
        return 0, 0

    return dx / norm, dy / norm


# Interpolation linéaire entre deux valeurs
def lerp(a, b, t):

    return a + (b - a) * t


# Renvoie True si deux positions sont sur la même case
def same_tile(x1, y1, x2, y2):

    return int(x1) == int(x2) and int(y1) == int(y2)


# Renvoie le centre d'une case (x, y) en coordonnées flottantes
def tile_center(x, y):

    return x + 0.5, y + 0.5


# Voisins d'une case (haut, bas, gauche, droite)
def get_neighbours(x, y):

    return [

        (x + 1, y),
        (x - 1, y),

        (x, y + 1),
        (x, y - 1)
    ]