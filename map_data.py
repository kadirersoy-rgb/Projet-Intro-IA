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
BBBBBBBBBBBBBBBBBBBB
BHHH    v   WWWWWW B
BHHH    v   WWWWWW B
BHHH  PFvFP WWWWWW B
E>>>>>>>X>>>>>>>>>>S
B       v          B
B CCCCC v CCCCCCCC B
B CCCCCPFvFPCCCCCC B
E>>>>>>>X>>>>>>>>>>S
B       v          B
BHHHHHH v  WWWWWW  B
BHHHHHHPFvFPWWWWWW B
E>>>>>>>X>>>>>>>>>>S
B       v          B
B CCCCC v CCCCCCCC B
B CCCCCPFvFPCCCCCC B
E>>>>>>>X>>>>>>>>>>S
B       v          B
BBBBBBBBBBBBBBBBBBBB
"""
