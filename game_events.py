
"""
    Projet Fit & Fun
    Autonabee

    Fabrikarium 2022 à Rennes
    code: Gweltaz Duval-Guennoc, Les Portes Logiques, Quimper
    contact: gweltou@hotmail.com
"""

"""
# Structure of a game event:

    (time, type, data)

# Type of events / Commands

    # - RPR   Set Rocks spawn prob  [0..1] TODO
    # - BPR   Set Bushes spawn prob [0..1] TODO
    # - WPR   Set Truncs spawn prob [0..1] TODO
    # - TPR   Set Trees spawn prob  [0..1] TODO
    - SS    Spawn Special Scenery (file_path, pos_x relatif au centre)
    # - DAM   Spawn dam TODO
    - BON   Spawn bonus tremplin
    - LVL_START   Level start (score recording, obstacles and bonuses spawning)
    # - LVL_STOP   Level stop TODO
    - LOCK    Lock control
    - UNLOCK    Enable control
    - FS    Fix speed (multiple of Vmax, 0 to disable)
    - OBS_ducks Duck obstacle.
        Args:
            zone d'apparition, en fraction de la hauteur de l'écran (float)
            direction (1 pour la droite, -1 pour la gauche)
            vitesse (float)
"""


zone_0 = 0.1666     # Fraction de la hauteur de l'écran
zone_1 = 0.5        # Fraction de la hauteur de l'écran
zone_2 = 0.8333     # Fraction de la hauteur de l'écran
right = 1
left = -1

game_events = [
    (0,     "LOCK"),                    # Bloque les controles du joueur
    (0,     "FS",   2),                 # Fixe la vitesse de défilement à 2 * VMax
    (0,     "SS",   ("3.png", 0)),      # Affiche le sprite "3.png" au centre de l'écran
    (1,     "SS",   ("2.png", 0)),      # Affiche le sprite "2.png" au centre de l'écran
    (2,     "SS",   ("1.png", 0)),      # Affiche le sprite "1.png" au centre de l'écran
    (3,     "SS",   ("go.png", 0)),     # Affiche le sprite "go.png" au centre de l'écran
    (4.6,   "FS",   0),                 # Vitesse de défilement normale
    (4.6,   "UNLOCK"),                  # Autorise les controles du joueur
    (4.6,   "LVL_START"),               # Commence le comptage du score et l'apparition d'obstacles
 
    # (6,     "OBS_duck", (zone_0, right, 1.0) ),
    # (6,     "OBS_duck" , (zone_2, left, 1.0) ),
    # (8,     "exemple_01")
]



event_blocks = {
    "tremplin_milieu": {
        "dur": 5,
        "events": [
            (0, "BON", zone_1)
        ]
    },

    "tremplin_haut": {
        "dur": 5,
        "events": [
            (0, "BON", zone_2)
        ]
    },

    "exemple_01": {
            "dur": 10,
            "events": [
                ( 0, "OBS_duck",    (zone_0, 1, 1.0) ),
                ( 0.5, "OBS_duck",  (zone_0 + 0.1, 1, 1.0) ),
                ( 0.5, "OBS_duck",  (zone_0 - 0.1, 1, 1.0) ),
                ( 2, "OBS_duck" ,   (zone_2, -1, 1.0) ),
                ( 2.5, "OBS_duck" , (zone_2 + 0.1, -1, 1.0) ),
                ( 2.5, "OBS_duck" , (zone_2 - 0.1, -1, 1.0) ),
                ],   
    },
    
    "exemple_02": {
            "dur": 10,
            "events": [
                ( 0, "OBS_duck",    (zone_2, 1, 1.0) ),
                ( 0.5, "OBS_duck",  (zone_2 + 0.1, 1, 1.0) ),
                ( 0.5, "OBS_duck",  (zone_2 - 0.1, 1, 1.0) ),
                ( 2, "OBS_duck" ,   (zone_0, -1, 1.0) ),
                ( 2.5, "OBS_duck" , (zone_0 + 0.1, -1, 1.0) ),
                ( 2.5, "OBS_duck" , (zone_0 - 0.1, -1, 1.0) ),
                ],   
    },
}
