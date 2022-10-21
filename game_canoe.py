import pygame as pg
import time
import os
import random
from console import Console
from game_entities import Player, Obstacle, Bonus, LandscapeProp

import psutil

class GameCanoe(Console):

    def __init__(self):
        super().__init__()        
    
    def game(self):
        """
        game panel. A character go headed on a scrolled side game depending
        on its speed. If it reaches muschroom the score is decrease.
        """

        prev_mem_usage =  psutil.Process().memory_info().rss / (1024 * 1024)

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
        duck_sprites = [pg.transform.rotozoom(pg.image.load(self.dir_img + "/duck.png"), 0, 1.5)]
        duck_sprites.append(pg.transform.flip(duck_sprites[0], True, False))
        bush_sprites = [pg.image.load(os.path.join(self.dir_img, f"buisson_{i}.png")) for i in range(1,3)]
        tree_sprites = [pg.image.load(os.path.join(self.dir_img, f"tree_{i}.png")) for i in range(1,3)]
        rock_sprites = [pg.image.load(os.path.join(self.dir_img, f"rocher_{i}.png")) for i in range(1,3)]
        truncs_sprites = [pg.image.load(os.path.join(self.dir_img, f"wood_{i}.png")) for i in range(1,3)]
        

        # Assets augmentation
        for elt in rock_sprites[:]:
            # Smaller rocks
            rock_sprites.append(pg.transform.scale(elt, (0.5, 0.5)))
        for elt in rock_sprites[:]:
            # Vertically flipped rocks
            rock_sprites.append(pg.transform.flip(elt, False, True))
        for elt in truncs_sprites[:]:
            # Smaller tree truncs
            truncs_sprites.append(pg.transform.scale(elt, (0.5, 0.5)))
        # Rotate all tree truncs
        truncs_sprites = [pg.transform.rotate(ws, random.choice([75, -70, 60, -50])) for ws in truncs_sprites]

        # Data
        previous_speed = 0  # Used for value smoothing
        bg_y = 0
        bonus_timer = 0
        distance = 0        # Virtual rowing distance (in bogo-meters)
        
        # Entities are instanciated once to avoid garbage collection as much as possible
        player = Player(self.screen)
        bonus = Bonus(self.screen)
        obstacles = [Obstacle(self.screen) for _ in range(3)]
        landscape = [LandscapeProp(self.screen) for _ in range(20)]

        mem_usage = psutil.Process().memory_info().rss / (1024 * 1024)
        print("memory usage:", round(mem_usage - prev_mem_usage, 2), "Mo")

        while True:
            time_delta = clock.tick(30)

            # Normalizing and smoothing speed value
            rot_speed_normalized = self.rot_speed / self.ROT_SPEED_MAX
            speed = SPEED_SMOOTHING * previous_speed + (1 - SPEED_SMOOTHING) * rot_speed_normalized
            previous_speed = speed
            player.speed = speed # speed is normalized (between 0 and 1)

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

            distance += scroll_speed * time_delta * 0.01

            # Background scrolling
            self.screen.blit(river_bg,(0, bg_y - self.size_y))
            self.screen.blit(river_bg,(0, bg_y))
            self.screen.blit(river_bg,(0, bg_y + self.size_y))
            # The scrolling speed depends on the player speed
            bg_y = bg_y + scroll_speed * time_delta
            if bg_y >= self.size_y:
                bg_y=0
            

            # Update all entities
            player.update(time_delta)
            bonus.update(time_delta)

            for elt in landscape:
                elt.update(time_delta, scroll_speed)

            for obs in obstacles:
                obs.update(time_delta)
            

            #########################################
            ## Obstacle/Player collision detection ##
            #########################################
            
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

            # Draw scenery elements in order defined by their layer
            landscape.sort(key=lambda x: x.layer)
            for elt in landscape:
                elt.draw()

            bonus.draw()
            player.draw()
            
            for obs in obstacles:
                obs.draw()
            
            
            # Spawn Lanscape elements
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
                        elt.spawn(random.choice(bush_sprites + truncs_sprites), 1)
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
                        
            # Spawn Obstacles and Bonuses
            if random.random() < 0.02:
                for obs in obstacles:
                    if not obs.alive:
                        side = 1
                        sprite = duck_sprites[0]
                        if random.random() < 0.5:
                            side = -1
                            sprite = duck_sprites[1]
                        
                        obstacle_height = random.random() * self.size_y
                        obs.spawn(sprite, obstacle_height, side)
                        break
            
            if not bonus.alive and random.random() < 0.002:
                bonus.spawn(random.random() * self.size_y)
            
            
            #####################
            ######## HUD ########
            #####################

            self.draw_text(self.get_banner(), 25, self.size_x/2, 1)
            self.draw_text(str(round(distance, 1)), 25, self.size_x - 32, self.size_y - 32)
            
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.menu()