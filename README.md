<<<<<<< HEAD
# Projet-IA-Pygames
=======
# Simulateur de trafic urbain 2D

Projet Python/Pygame de simulation de circulation urbaine sur une grille 2D.

Le but est de reprendre la logique du TP `SimStore` dans un contexte de ville :

- agents autonomes,
- machine a etats,
- carte de distances,
- embouteillage
- comportements emergents.

La simulation contient des voitures, des pietons, des feux de circulation, des passages pietons, des bouchons et des periodes de la journee.

## Lancer le projet

Installer les dependances si besoin :

```bash
pip install pygame numpy
```

Puis lancer :

```bash
python main.py
```

Touches utiles :

- `Espace` : pause / reprise.
- Fermer la fenetre Pygame : quitter.

## Principe general

La ville est une grille. Chaque case contient un symbole de carte :

| Symbole | Role |
| --- | --- |
| `B` | batiment |
| `H` | habitation |
| `W` | travail / bureaux |
| `C` | centre-ville |
| `>` | route a sens unique vers la droite |
| `<` | route a sens unique vers la gauche |
| `^` | route a sens unique vers le haut |
| `v` | route a sens unique vers le bas |
| `X` | carrefour |
| `P` | passage pieton |
| `F` | feu |
| `E` | entree de ville |
| `S` | sortie de ville |
| espace | trottoir / zone pietonne |

Les voitures utilisent uniquement les routes. Les pietons utilisent les trottoirs et les passages pietons.

## Architecture des fichiers

| Fichier | Role |
| --- | --- |
| `main.py` | Point d'entree. Initialise Pygame, cree `GameData`, `Renderer`, `Simulation`, puis lance la boucle principale. |
| `settings.py` | Constantes du projet : FPS, taille des cases, vitesses, durees des feux, etats des agents, symboles de carte. |
| `colors.py` | Couleurs des routes, batiments, feux, agents et niveaux de trafic. |
| `map_data.py` | Carte texte de la ville. C'est ici qu'on modifie le plan urbain. |
| `game_data.py` | Donnees centrales : carte, routes, zones speciales, densite, occupation des cases, distance maps, regles de circulation. |
| `simulation.py` | Moteur de simulation : update des agents, periodes de la journee, feux, densite. |
| `spawner.py` | Creation des voitures et pietons selon la periode de la journee. |
| `vehicle.py` | IA des voitures : machine a etats, suivi de distance map, feux, bouchons, file indienne. |
| `pedestrian.py` | IA des pietons : marche, attente au feu, passage pieton, distance map pietonne. |
| `traffic_light.py` | Feux coordonnes horizontal/vertical et feu pieton. |
| `renderer.py` | Affichage Pygame : carte, routes, passages pietons, voitures, pietons, feux, interface. |
| `pathfinding.py` | Compatibilite avec l'ancien point d'entree de pathfinding. Redirige vers `GameData.get_distance_map`. |
| `utils.py` | Fonctions utilitaires generales. |

## Machine a etats

Les voitures ont plusieurs etats definis dans `settings.py` :

| Etat | Signification |
| --- | --- |
| `STATE_DRIVE` | La voiture roule normalement. |
| `STATE_BRAKE` | La voiture freine car une case est reservee/bloquee. |
| `STATE_RED_LIGHT` | La voiture attend un feu rouge. |
| `STATE_TRAFFIC_JAM` | La voiture est dans un bouchon. |
| `STATE_EXIT` | La voiture a termine ses missions et quitte la ville. |
| `STATE_FOLLOW` | La voiture suit une voiture devant elle sans entrer dans sa case. |

Les pietons ont aussi leurs etats :

| Etat | Signification |
| --- | --- |
| `STATE_WALK` | Le pieton marche. |
| `STATE_WAIT_LIGHT` | Le pieton attend au feu. |
| `STATE_CROSS` | Le pieton traverse. |
| `STATE_PEDESTRIAN_EXIT` | Le pieton a termine sa mission. |

## Distance maps

Le pathfinding fonctionne avec des cartes de distances, comme dans `SimStoreVfinale`.

Dans `game_data.py`, `get_distance_map(target, profile)` renvoie une grille de distances vers une cible.

Il existe deux profils :

- `vehicle` : suit uniquement les routes et respecte les sens uniques.
- `pedestrian` : suit les trottoirs et passages pietons.

Les voitures regardent les voisins possibles, puis choisissent la case dont la distance vers la cible est la plus faible.

## Voitures

Les voitures :

- apparaissent aux entrees `E`,
- ont 3 targets comme dans `SimStoreVfinale`,
- utilisent une distance map pour aller vers leur target courante,
- respectent les sens uniques,
- respectent les feux horizontal/vertical,
- ne se chevauchent pas : maximum 1 voiture par case,
- attendent en file indienne si une voiture devant est arretee,
- ralentissent en fonction de la densite,
- quittent la ville apres leurs missions.

Important : une voiture qui s'arrete est recentree au milieu de sa case.

## Pietons

Les pietons :

- apparaissent sur les zones pietonnes,
- utilisent aussi une distance map,
- traversent uniquement sur les passages pietons,
- respectent les feux pietons,
- sont prioritaires sur un passage deja occupe.

Les voitures ne rentrent pas sur un passage pieton occupe.

## Feux

Les feux sont coordonnes dans `traffic_light.py`.

Ils alternent entre deux axes :

1. `H_GREEN` : circulation horizontale autorisee, verticale bloquee.
2. `H_ORANGE` : transition horizontale.
3. `V_GREEN` : circulation verticale autorisee, horizontale bloquee.
4. `V_ORANGE` : transition verticale.

Le feu pieton est calcule en fonction de l'axe du passage pieton.

## Periodes de la journee

La simulation alterne automatiquement :

1. `MATIN`
2. `APRES-MIDI`
3. `SOIR`

Chaque periode dure `DAY_PERIOD_DURATION` secondes.

Effets principaux :

- matin : trafic fort, deplacements vers travail et centre-ville ;
- apres-midi : trafic plus calme et varie ;
- soir : retour vers habitations ou sortie de ville.

## Modifier la carte

La carte est dans `map_data.py`, variable `CITY_MAP`.

Regles importantes :

- toutes les lignes doivent avoir la meme longueur ;
- `>` `<` `^` `v` sont des routes a sens unique ;
- les voitures ne peuvent pas rouler hors des routes ;
- les pietons ont besoin de trottoirs ou passages pietons ;
- les feux `F` doivent etre places pres des carrefours/passages.

## Points importants pour comprendre le code

- La logique centrale est dans `GameData`.
- Les agents ne connaissent pas toute la ville directement : ils demandent a `GameData` les voisins, les distances, les feux et les occupations.
- Les comportements emergents viennent de regles simples :
  - une voiture par case,
  - distance map vers la cible,
  - attente aux feux,
  - priorite pieton,
  - file indienne,
  - spawn variable selon la periode.

## Tests rapides

Verifier que les fichiers compilent :

```bash
python -m py_compile main.py renderer.py simulation.py game_data.py vehicle.py pedestrian.py traffic_light.py spawner.py settings.py colors.py map_data.py utils.py pathfinding.py
```

Lancer la simulation :

```bash
python main.py
```

>>>>>>> origin/master
