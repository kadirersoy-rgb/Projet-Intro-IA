# settings.py

##########################################################################
# PARAMÈTRES GÉNÉRAUX
##########################################################################

# Taille d'une case de la grille en pixels
ZOOM = 28

# Nombre d'images par seconde
FPS = 60

##########################################################################
# PÉRIODES DE LA JOURNÉE
##########################################################################

# Chaque période dure 20 secondes
DAY_PERIOD_DURATION = 20

# Noms des périodes
MORNING = "MATIN"
AFTERNOON = "APRES-MIDI"
EVENING = "SOIR"

# Ordre des périodes
DAY_PERIODS = [
    MORNING,
    AFTERNOON,
    EVENING
]

# Intensité de spawn selon la période
TRAFFIC_INTENSITY = {
    MORNING: 1.5,      # beaucoup de monde le matin
    AFTERNOON: 0.4,    # trafic plus calme
    EVENING: 1.8       # beaucoup de monde le soir
}

##########################################################################
# LIMITES D'AGENTS
##########################################################################

MAX_VEHICLES = 200
MAX_PEDESTRIANS = 100

##########################################################################
# VITESSES
##########################################################################

VEHICLE_SPEED = 2.0
PEDESTRIAN_SPEED = 1.0

# Densité maximale avant blocage
MAX_DENSITY = 8

# Influence de la densité dans le choix de chemin
DENSITY_AVOIDANCE_WEIGHT = 1.8

# Ralentissement progressif selon la densité locale
TRAFFIC_SLOWDOWN_FACTOR = 0.35

# Distance de securite : une voiture reserve la case ou elle se rend.
VEHICLE_RESERVES_NEXT_TILE = True

# La creation de voitures ralentit quand la ville est congestionnee.
MIN_TRAFFIC_FLOW_FACTOR = 0.25

# Petite penalite pour limiter les changements de direction trop nerveux.
VEHICLE_TURN_PENALTY = 0.35

##########################################################################
# DURÉES DES FEUX
##########################################################################

GREEN_LIGHT_DURATION = 6
ORANGE_LIGHT_DURATION = 2
RED_LIGHT_DURATION = 6

# Probabilite qu'une voiture decide de s'arreter au feu orange.
ORANGE_LIGHT_STOP_PROBABILITY = 0.55

##########################################################################
# SYMBOLES DE LA MAP
##########################################################################

# Routes directionnelles
ROAD_RIGHT = '>'
ROAD_LEFT = '<'
ROAD_UP = '^'
ROAD_DOWN = 'v'

# Éléments de ville
CROSSROAD = 'X'
BUILDING = 'B'
SPAWN = 'E'
EXIT = 'S'
PEDESTRIAN_WAY = 'P'
TRAFFIC_LIGHT = 'F'
EMPTY = ' '

##########################################################################
# ÉTATS DES VOITURES
##########################################################################

STATE_DRIVE = 100
STATE_BRAKE = 101
STATE_RED_LIGHT = 102
STATE_TRAFFIC_JAM = 103
STATE_EXIT = 104
STATE_FOLLOW = 105

# Quand la voiture devant roule encore, on avance un peu dans la case
# sans entrer dans la case occupee.
VEHICLE_FOLLOW_OFFSET = 0.18

##########################################################################
# ÉTATS DES PIÉTONS
##########################################################################

STATE_WALK = 200
STATE_WAIT_LIGHT = 201
STATE_CROSS = 202
STATE_PEDESTRIAN_EXIT = 203

##########################################################################
# AFFICHAGE
##########################################################################

SHOW_GRID = True

# Largeur reservee a droite pour la legende.
LEGEND_PANEL_WIDTH = 320

# Largeur minimale de la fenetre pour laisser respirer la carte et la legende.
MIN_WINDOW_WIDTH = 960

# Hauteur minimale de la fenetre quand la carte est petite.
MIN_WINDOW_HEIGHT = 720
