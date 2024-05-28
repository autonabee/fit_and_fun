# This file is a part of Fit & Fun
#
# Copyright (C) 2023 Inria/Autonabee
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

"""
    Projet Fit & Fun
    Autonabee

    Fabrikarium 2022 à Rennes
    code: Gweltaz Duval-Guennoc, Les Portes Logiques, Quimper
    contact: gweltou@hotmail.com
"""

"""
# Structure of a game event:

    (time, type, data) #(temps en seconde, type d'objet apparant (image), emplacement sur lécran)

# Type of events / Commands

    # - RPR   Set Rocks spawn prob  [0..1] TODO
    # - BPR   Set Bushes spawn prob [0..1] TODO
    # - WPR   Set Truncs spawn prob [0..1] TODO
    # - TPR   Set Trees spawn prob  [0..1] TODO
    - DECO    Spawn Special Scenery (file_path, pos_x relatif au centre)
    # - DAM   Spawn dam TODO
    - BONUS   Spawn bonus tremplin
    - LVL_START   Level start (score recording, obstacles and bonuses spawning)
    # - LVL_STOP   Level stop TODO
    - LOCK    Lock control
    - UNLOCK    Enable control
    - FS    Fix speed (multiple of Vmax, 0 to disable)
    - OBS_ducks Duck obstacle.
        Data:
            sprite du canard, 0=parent, 1=enfant (int)
            zone d'apparition, en fraction de la hauteur de l'écran (float)
            direction (1 pour la droite, -1 pour la gauche)
            vitesse, multiple de la vitesse par défaut (float)
"""


zone_0 = 0.1666     # Fraction de la hauteur de l'écran, en partant du bas
zone_1 = 0.5        # Fraction de la hauteur de l'écran
zone_2 = 0.8333     # Fraction de la hauteur de l'écran
right = 1
left = -1

# C'est par la liste ci-dessous qu'on ajoute des événements au jeu
# On peut ajouter des entrées manuellement, au format: (temps, type, [données supp])
# On peut aussi ajouter des blocs d'évènements depuis le dictionnaire `event_blocks` en y mettant le nom du bloc d'évenement
#   ex: (16.6, "tremplin_milieu"),
# Les évènements et blocs d'évènements peuvent être ajoutés à la liste avant le début de la partie ou en cours de partie
# Lors de l'ajout de blocs d'évènement à la liste la durée du bloc (paramètre "dur") doit être pris en compte pour décaller les marqueurs
#   temporels des prochains évènements afin d'éviter les chevauchements d'évènements.
# Ne pas oublier de trier la liste d'évènements en ordre temporel après tout ajout.
# Ex:
    # ev_block = random.choice(list(event_blocks.values()))
    # events = [ (t + te, *ev) for te, *ev in ev_block["events"] ]
    # game_events.extend(events)
    # cooldown = ev_block["dur"]
    # game_events.sort(key=lambda x: x[0])    # Sort by time


start_events = [
    (0,     "LOCK"),                    # Bloque les controles du joueur
    (0,     "FS",   3),                 # Fixe la vitesse de défilement à 2 * VMax
    (0,     "DECO",   ("3.png", 0)),    # Affiche le sprite "3.png" au centre de l'écran
    (1,     "DECO",   ("2.png", 0)),    # Affiche le sprite "2.png" au centre de l'écran
    (2,     "DECO",   ("1.png", 0)),    # Affiche le sprite "1.png" au centre de l'écran
    (3,     "DECO",   ("go.png", 0)),   # Affiche le sprite "go.png" au centre de l'écran
    (4.6,   "FS",   6),                 # Vitesse de défilement normale
    (4.6,   "UNLOCK"),                  # Autorise les controles du joueur
    (4.6,   "LVL_START"),               # Commence le comptage du score et l'apparition d'obstacles
]



#### DICTIONNAIRE DE BLOCS D'EVENEMENTS ####

# La durée des blocs d'évènements (paramètre 'dur' en secondes) est à régler manuellement et devrait inclure
#   une période de repos pour éviter les enchaînement d'évènements trop serrés
#   ( La structure peut faire penser à du JSON mais c'est du Python ! ;) )

event_blocks = {
    "tremplin_milieu": {
        "dur": 5,
        "events": [
            (0, "BONUS", zone_1)
        ]
    },
    "tremplin_haut": {
        "dur": 5,
        "events": [
            (0, "BONUS", zone_2)
        ]
    },

    "exemple_01": {
            # Un groupe de canard vient en bas depuis la gauche,
            # Suivi d'un autre groupe en haut depuis la droite, 2s plus tard
            "dur": 10,
            "events": [
                ( 0,    "OBS_duck",     (0, zone_0, right, 1.0) ),
                ( 0.8,  "OBS_duck",     (1, zone_0 + 0.1, right, 1.0) ),
                ( 0.8,  "OBS_duck",     (1, zone_0 - 0.1, right, 1.0) ),
                ( 2,    "OBS_duck" ,    (0, zone_2, left, 1.0) ),
                ( 2.8,  "OBS_duck" ,    (1, zone_2 + 0.1, left, 1.0) ),
                ( 2.8,  "OBS_duck" ,    (1, zone_2 - 0.1, left, 1.0) ),
                ],   
    },
    
    "exemple_02": {
            "dur": 10,
            "events": [
                ( 0, "OBS_duck",    (0, zone_2, right, 1.0) ),
                ( 0.8, "OBS_duck",  (1, zone_2 + 0.1, right, 1.0) ),
                ( 0.8, "OBS_duck",  (1, zone_2 - 0.1, right, 1.0) ),
                ( 2, "OBS_duck" ,   (0, zone_0, left, 1.0) ),
                ( 2.8, "OBS_duck" , (1, zone_0 + 0.1, left, 1.0) ),
                ( 2.8, "OBS_duck" , (1, zone_0 - 0.1, left, 1.0) ),
                ],   
    },

    "omg_birds": {
        "dur": 10,
        "events": [
            # for i in range(32): 
            #     print(f'( {round(random.random()*2+1.8, 2)}, "OBS_duck", (1, {round(zone_0+2*(random.random()-0.5)*zone_0,2)}, right, {round(4+2*random.random(),2)}) ),') 
            (0, "OBS_duck", (0, zone_0, right, 1.5) ),
            ( 3.6, "OBS_duck", (1, 0.23, right, 4.55) ),
            ( 3.11, "OBS_duck", (1, 0.24, right, 4.32) ),
            ( 3.39, "OBS_duck", (1, 0.13, right, 4.75) ),
            ( 2.55, "OBS_duck", (1, 0.16, right, 4.16) ),
            ( 3.05, "OBS_duck", (1, 0.12, right, 4.01) ),
            ( 1.85, "OBS_duck", (1, 0.3, right, 5.34) ),
            ( 3.77, "OBS_duck", (1, 0.03, right, 5.05) ),
            ( 2.17, "OBS_duck", (1, 0.29, right, 4.51) ),
            ( 2.17, "OBS_duck", (1, 0.25, right, 5.01) ),
            ( 2.32, "OBS_duck", (1, 0.1, right, 5.0) ),
            ( 2.24, "OBS_duck", (1, 0.28, right, 5.19) ),
            ( 2.38, "OBS_duck", (1, 0.24, right, 5.26) ),
            ( 3.46, "OBS_duck", (1, 0.06, right, 4.8) ),
            ( 1.92, "OBS_duck", (1, 0.0, right, 5.65) ),
            ( 2.77, "OBS_duck", (1, 0.01, right, 4.42) ),
            ( 3.0, "OBS_duck", (1, 0.27, right, 4.09) ),
            ( 1.83, "OBS_duck", (1, 0.03, right, 5.78) ),
            ( 2.07, "OBS_duck", (1, 0.18, right, 5.32) ),
            ( 3.14, "OBS_duck", (1, 0.07, right, 4.93) ),
            ( 2.41, "OBS_duck", (1, 0.01, right, 5.45) ),
            ( 2.23, "OBS_duck", (1, 0.16, right, 4.59) ),
            ( 2.3, "OBS_duck", (1, 0.32, right, 4.48) ),
            ( 2.47, "OBS_duck", (1, 0.05, right, 5.95) ),
            ( 1.9, "OBS_duck", (1, 0.27, right, 5.31) ),
            ( 3.09, "OBS_duck", (1, 0.08, right, 4.04) ),
            ( 2.46, "OBS_duck", (1, 0.17, right, 4.32) ),
            ( 3.22, "OBS_duck", (1, 0.33, right, 4.37) ),
            ( 3.55, "OBS_duck", (1, 0.29, right, 4.83) ),
            ( 2.65, "OBS_duck", (1, 0.11, right, 4.9) ),
            ( 3.36, "OBS_duck", (1, 0.28, right, 5.8) ),
            ( 2.5, "OBS_duck", (1, 0.17, right, 4.64) ),
            ( 1.88, "OBS_duck", (1, 0.02, right, 4.65) ),
        ]
    }
}
