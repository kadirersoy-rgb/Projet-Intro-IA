# pathfinding.py


def compute_distance_map(game, target, profile="vehicle"):
    """
    Compatibilite avec l'ancien point d'entree.
    La logique principale vit dans GameData pour partager le cache.
    """

    return game.get_distance_map(target, profile).copy()
