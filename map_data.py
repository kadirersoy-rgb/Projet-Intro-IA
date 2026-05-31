# map_data.py

##########################################################################
# CARTE DE LA VILLE
#
# Chaque caractère correspond à une tuile.
#
# B = bâtiment
# H = habitation
# W = travail / bureaux
# C = centre-ville
#
# > = route vers la droite
# < = route vers la gauche
# ^ = route vers le haut
# v = route vers le bas
#
# X = carrefour
# P = passage piéton
# F = feu
#
# E = entrée de ville
# S = sortie de ville
#
# IMPORTANT :
# toutes les lignes doivent avoir exactement le même nombre de caractères.
##########################################################################

CITY_MAP = """
BBBBBBBBBSBBBBBBSBBBBBBSBBBBBBB
B        ^      ^      ^      B
B        ^      ^      ^      B
B        ^      ^      ^      B
B  HH HH ^ CC C ^ CC C ^ WW W B
B  HHHH  ^ CCC  ^ CCC  ^ WWWW B
E>>>>>>PFX>>>>PFX>>>>PFX>>>>>>S
B        F      F      F      B
B        P      P      P      B
B  HH HH ^ CC C ^ CC C ^ WW W B
B  HHHH  ^ CCC  ^ CCC  ^ WWWW B
E>>>>>>PFX>>>>PFX>>>>PFX>>>>>>S
B        F      F      F      B
B        P      P      P      B
B  HH HH ^ CC C ^ CC C ^ WW W B
B  HHHH  ^ CCC  ^ CCC  ^ WWWW B
E>>>>>>PFX>>>>PFX>>>>PFX>>>>>>S
B        F      F      F      B
B        P      P      P      B
B  HH HH ^ CC C ^ CC C ^ WW W B
B  HHHH  ^ CCC  ^ CCC  ^ WWWW B
E>>>>>>PFX>>>>PFX>>>>PFX>>>>>>S
B        F      F      F      B
B        P      P      P      B
B  HH HH ^ CC C ^ CC C ^ WW W B
B  HHHHH ^ CCCC ^ CCCC ^ WWWW B
B  HHHHH ^ CCCC ^ CCCC ^ WWWW B
B        ^      ^      ^      B
BBBBBBBBBEBBBBBBEBBBBBBEBBBBBBB
"""
