
"""
# Type of events

- RPR   Set Rocks spawn prob  [0..1]
- BPR   Set Bushes spawn prob [0..1]
- WPR   Set Truncs spawn prob [0..1]
- TPR   Set Trees spawn prob  [0..1]
- SS    Spawn Special Scenery (file_path, pos_x relatif au centre)
- DAM   Spawn dam
- BON   Spawn bonus tremplin
- LV1   Level start (score recording, obstacles and bonuses spawning)
- LV0   Level stop
- LC    Lock control
- EC    Enable control
- FS    Fix speed (multiple of Vmax, 0 to disable)


    Structure of a game event:
        (distance, type, data)
    
    Distance:
        in meters, from the starting point
    
    Type:
        
    
    Data:
        Can be empty
        Can be a tupple
"""

game_events = [
    (0,     "LC"),                      # Bloque les controles du joueur
    (0,     "FS",   2),                 # Fixe la vitesse de défilement à 2 * VMax
    (0,     "SS",   ("3.png", 0)),      # Affiche le sprite "3.png" au centre de l'écran
    (5,     "SS",   ("2.png", 0)),      # Affiche le sprite "2.png" au centre de l'écran
    (10,    "SS",   ("1.png", 0)),      # Affiche le sprite "1.png" au centre de l'écran
    (15,    "SS",   ("go.png", 0)),     # Affiche le sprite "go.png" au centre de l'écran
    (22,    "FS",   0),                 # Vitesse de défilement normale
    (22,    "EC"),                      # Autorise les controles du joueur
    (22,    "LV1"),                     # Commence le comptage du score et l'apparition d'obstacles
]
