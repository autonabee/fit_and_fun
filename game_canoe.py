"""
    Projet Fit & Fun
    Autonabee

    Fabrikarium 2022 à Rennes
    code: Gweltaz Duval-Guennoc, Les Portes Logiques, Quimper
    contact: gweltou@hotmail.com
"""


import pygame as pg
import time
import os
import random
from console import Console
from game_entities import Player, Obstacle, Bonus, LandscapeProp
from game_events import game_events, event_blocks


class GameCanoe(Console):

    def __init__(self):
        super().__init__()        
    
    def game(self):
        """
        game panel. A character go headed on a scrolled side game depending
        on its speed. If it reaches muschroom the score is decrease.
        """

        # Constants
        SCROLL_SPEED_MAX = 0.2      # Raise value for a faster river current
        SCROLL_SPEED_MIN = 0.02     # Minimum current speed of the river
        SPEED_SMOOTHING = 0.8       # To smooth speed value and avoid jagginess, between 0 and 1
        BONUS_DURATION = 2.0        # Duration of speed bonus with doubled scrolling speed (in seconds)
        BONUS_COOLDOWN = 1.0        # Speed bonus deceleration period (in seconds)


        # Time init
        clock = pg.time.Clock()
        self.time0=time.time()

        # Loading sprite assets
        river_bg = pg.image.load(self.dir_img+'/level_bg.png')
        duck_sprites = [pg.image.load(os.path.join(self.dir_img, f"canard_{i}.png")) for i in range(1,3)]
        # duck_sprites = [pg.transform.rotozoom(pg.image.load(self.dir_img + "/duck.png"), 0, 1.5)]
        # duck_sprites.append(pg.transform.flip(duck_sprites[0], True, False))
        bush_sprites = [pg.image.load(os.path.join(self.dir_img, f"buisson_{i}.png")) for i in range(1,3)]
        tree_sprites = [pg.image.load(os.path.join(self.dir_img, f"tree_{i}.png")) for i in range(1,3)]
        rock_sprites = [pg.image.load(os.path.join(self.dir_img, f"rocher_{i}.png")) for i in range(1,4)]
        trunc_sprites = [pg.image.load(os.path.join(self.dir_img, f"wood_{i}.png")) for i in range(1,3)]

        # Assets augmentation
        duck_sprites_aug = []
        for s in duck_sprites:
            # Resized and mirrored
            #resized = pg.transform.rotozoom(s, 0, 1.25)
            flipped = pg.transform.flip(s, True, False)
            duck_sprites_aug.append(s)
            duck_sprites_aug.append(flipped)
        duck_sprites = duck_sprites_aug
        for elt in rock_sprites[:]:
            # Smaller rocks
            rock_sprites.append(pg.transform.scale(elt, (0.5, 0.5)))
        for elt in rock_sprites[:]:
            # Vertically flipped rocks
            rock_sprites.append(pg.transform.flip(elt, False, True))
        for elt in trunc_sprites[:]:
            # Smaller tree truncs
            trunc_sprites.append(pg.transform.scale(elt, (0.5, 0.5)))
        # Rotate all tree truncs
        trunc_sprites = [pg.transform.rotate(ws, random.choice([75, -70, 60, -50])) for ws in trunc_sprites]

        # Data
        previous_speed = 0  # Used for value smoothing
        bg_y = 0
        bonus_timer = 0
        distance = 0        # Virtual rowing distance (in bogo-meters)
        event_idx = 0       # Keep track of game events
        # level_started = False
        control_enabled = True
        fixed_speed = 0
        
        # Entities are instanciated once to avoid garbage collection as much as possible
        player = Player(self.screen)
        bonus = Bonus(self.screen)  # Only one bonus at each moment
        obstacles = [Obstacle(self.screen) for _ in range(16)]
        landscape = [LandscapeProp(self.screen) for _ in range(32)]
        special_scenery = [LandscapeProp(self.screen) for _ in range(8)]

        # Level events
        # Ici on peut ajouter des évenements temporels au niveau, créés à la volée
        # ou bien piochés dans le dictionnaire `event_blocks`, du fichier `game_events.py`
        # Ne pas oublier de trier la liste `game_events` après tout ajout
        # On peut aussi ajouter un bloc d'évenements à la liste en cours de partie...

        t = 10
        for i in range(10):
            ev_block = random.choice(list(event_blocks.values()))
            events = [ (t + te, *ev) for te, *ev in ev_block["events"] ]
            game_events.extend(events)
            t += ev_block["dur"]

        game_events.sort(key=lambda x: x[0])    # Sort by time

        while True:
            time_delta = clock.tick(30)

            ####  Scripted Game Events (see file game_events.py)  ####
            if event_idx < len(game_events):
                t = time.time() - self.time0
                while game_events[event_idx][0] < t:
                    event_type = game_events[event_idx][1]
                    if event_type == "LOCK":      # Lock game control
                        control_enabled = False
                    elif event_type == "UNLOCK":    # Enable game control
                        control_enabled = True
                    elif event_type == "FS":    # Fixed speed
                        event_data = game_events[event_idx][2]
                        fixed_speed = event_data
                    elif event_type == "LVL_START":     # Start level (obstacles, bonuses and score recording)
                        level_started = True
                    elif event_type == "DECO":      # Spawn special scenery
                        event_data = game_events[event_idx][2]
                        for elt in special_scenery:
                            if not elt.alive:
                                sprite_filename = os.path.join(self.dir_img, event_data[0])
                                sprite = pg.image.load(sprite_filename)
                                elt.spawn(sprite, 0)
                                elt.pos_x = self.size_x * 0.5 + event_data[1]
                                break
                        else:
                            print("WARNING: special_scenery array is full")
                    elif event_type == "BONUS":
                        h = game_events[event_idx][2]
                        bonus_height = self.size_y * (1.0 - h)
                        bonus.spawn(bonus_height)
                    elif event_type == "OBS_duck":
                        indiv, h, dir, speed = game_events[event_idx][2]
                        for obs in obstacles:
                            if not obs.alive:
                                side = dir
                                if side >= 0:
                                    sprite = duck_sprites[indiv*2 + 0] # facing right
                                else:
                                    sprite = duck_sprites[indiv*2 + 1] # facing left
                                
                                spawn_height = self.size_y * (1.0 - h)
                                obs.spawn(sprite, spawn_height, side, speed)
                                break
                        else:
                            print("WARNING: obstacle array is full")
                    else:
                        if event_type in event_blocks:
                            events = event_blocks[event_type]["events"]
                            events = [ (t + te, *ev) for te, *ev in events ]
                            game_events.extend(events)
                            game_events.sort(key=lambda x: x[0])    # Sort by time
                        else:
                            print("ERROR: event type '{}' not found in event_blocks".format(event_type))
                    event_idx += 1
                    if event_idx >= len(game_events):
                        break


            # Normalizing and smoothing speed value
            if control_enabled:
                rot_speed_normalized = self.rot_speed / self.ROT_SPEED_MAX
            else:
                rot_speed_normalized = 0
            speed = SPEED_SMOOTHING * previous_speed + (1 - SPEED_SMOOTHING) * rot_speed_normalized
            previous_speed = speed
            player.speed = speed # speed is normalized (between 0 and 1)

            ####  Speed Bonus  ####
            if bonus_timer > 0:
                # Bonus is activated
                if bonus_timer > BONUS_COOLDOWN*1000:
                    # Full speed
                    scroll_speed = 2 * SCROLL_SPEED_MAX
                else:
                    # Decelerating by interpolating between double speed and regular speed
                    a = bonus_timer/(BONUS_COOLDOWN*1000)
                    scroll_speed = a * 2 * SCROLL_SPEED_MAX + (1-a) * (SCROLL_SPEED_MAX * speed + SCROLL_SPEED_MIN)
                bonus_timer -= time_delta
            else:
                scroll_speed = SCROLL_SPEED_MAX * speed + SCROLL_SPEED_MIN
            
            if fixed_speed > 0:
                scroll_speed = fixed_speed * SCROLL_SPEED_MAX

            distance += scroll_speed * time_delta * 0.01

            ####  Background scrolling  ####
            self.screen.blit(river_bg,(0, bg_y - self.size_y))
            self.screen.blit(river_bg,(0, bg_y))
            self.screen.blit(river_bg,(0, bg_y + self.size_y))
            # The scrolling speed depends on the player speed
            bg_y = bg_y + scroll_speed * time_delta
            if bg_y >= self.size_y:
                bg_y=0
            

            ####  Update all entities  ####
            player.update(time_delta)
            bonus.update(time_delta)

            for elt in landscape:
                elt.update(time_delta, scroll_speed)

            for elt in special_scenery:
                elt.update(time_delta, scroll_speed)

            for obs in obstacles:
                obs.update(time_delta)
            

            ####  Obstacle/Player collision detection  ####          
            colliding = player.hitbox.collidelistall([o.hitbox for o in obstacles if o.alive])
            if len(colliding) > 0:
                was_hit = player.hit()
                if was_hit:
                    self.score -= 100
            for i in colliding:
                obstacles[i].alive = False
            
            if bonus.alive and player.hitbox.colliderect(bonus.hitbox):
                bonus.alive = False
                bonus_timer = (BONUS_DURATION + BONUS_COOLDOWN) * 1000
                self.score += 200

            for elt in special_scenery:
                elt.draw()

            # Draw landscape elements in order defined by their layer
            landscape.sort(key=lambda x: x.layer)
            for elt in landscape:
                elt.draw()

            bonus.draw()
            player.draw()
            
            for obs in obstacles:
                obs.draw()
            
            
            ####  Spawning Lanscape elements  ####
            if random.random() < 0.05:
                # Spawn rocks on bottom layer
                for elt in landscape:
                    if not elt.alive:
                        elt.spawn(random.choice(rock_sprites), 0)
                        break
            if random.random() < 0.01:
                # Spawn tree truncs
                for elt in landscape:
                    if not elt.alive:
                        elt.spawn(random.choice(bush_sprites + trunc_sprites), 1)
                        break
            if random.random() < 0.01:
                # Spawn bushes
                for elt in landscape:
                    if not elt.alive:
                        elt.spawn(random.choice(bush_sprites), 2)
                        break
            if random.random() < 0.01:
                # Spawn trees on highest layer
                for elt in landscape:
                    if not elt.alive:
                        elt.spawn(random.choice(tree_sprites), 3)
                        break
            
            
            ####  HUD  ####
            self.draw_text(self.get_banner(), 25, self.size_x/2, 1)
            self.draw_text(str(round(distance, 1)), 25, self.size_x - 32, self.size_y - 32)
            
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.menu()