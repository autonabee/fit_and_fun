import pygame as pg
import time
import os
import random
from console import Console
from game_entities import Player, Obstacle, Bonus, LandscapeProp


class GameCanoe(Console):

    def __init__(self, wind):
        super().__init__(wind)
    
    def game(self):
        """
        game panel. A character go headed on a scrolled side game depending
        on its speed. If it reaches muschroom the score is decrease.
        """
        # Time init
        clock = pg.time.Clock()
        self.reset_data()

        # Sprite assets loading
        river_bg = pg.image.load(self.dir_img+'/level_bg.png')
        #river_bg = pg.transform.scale(river_bg, (self.size_x, self.size_y))
        duck_sprites = [pg.transform.rotozoom(pg.image.load(self.dir_img + "/duck.png"), 0, 1.5)]
        duck_sprites.append(pg.transform.flip(duck_sprites[0], True, False))
        bush_sprites = [pg.image.load(os.path.join(self.dir_img, f"buisson_{i}.png")) for i in range(1,3)]
        tree_sprites = [pg.image.load(os.path.join(self.dir_img, f"tree_{i}.png")) for i in range(1,3)]
        rock_sprites = [pg.image.load(os.path.join(self.dir_img, f"rocher_{i}.png")) for i in range(1,3)]
        wood_sprites = [pg.image.load(os.path.join(self.dir_img, f"wood_{i}.png")) for i in range(1,3)]
        wood_sprites = [pg.transform.rotate(ws, random.choice([75, -75])) for ws in wood_sprites]
        
        player = Player(self.screen)
        
        # Data
        last_speed = 0  # Used for value smoothing
        bg_y = 0
        bg_scroll_speed = 0.1
        
        # Create prop pools
        # Entities are instanciated once to avoid constant garbage collection
        obstacles = [Obstacle(self.screen) for _ in range(3)]
        lower_landscape = [LandscapeProp(self.screen) for _ in range(5)]
        upper_landscape = [LandscapeProp(self.screen) for _ in range(2)]
        
        bonus = Bonus(self.screen)

        while True:
            delta = clock.tick(30)

            # Background scrolling
            self.screen.blit(river_bg,(0, bg_y - self.size_y))
            self.screen.blit(river_bg,(0, bg_y))
            self.screen.blit(river_bg,(0, bg_y + self.size_y))
            bg_y = bg_y + bg_scroll_speed * delta
            if bg_y >= self.size_y:
                bg_y=0
            
            # Normalizing and smoothing
            speed =  0.8 * last_speed + 0.2 * (self.rot_speed / self.ROT_SPEED_MAX)
            last_speed = speed
            # Speed should be normalized    
            player.speed = speed

            # Update all entities
            player.update(delta)

            for le in lower_landscape + upper_landscape:
                le.update(delta, bg_scroll_speed)

            bonus.update(delta)

            for obs in obstacles:
                obs.update(delta)
            
            #########################################
            ## Obstacle/Player collision detection ##
            #########################################
            
            #collision = player_hitbox.collideobjects(obstacles, key=lambda x: x.hitbox)
            colliding = player.hitbox.collidelistall([o.hitbox for o in obstacles if o.alive])
            if len(colliding) > 0:
                was_hit = player.hit()
                if was_hit:
                    self.score -= 100
            for i in colliding:
                obstacles[i].alive = False
            
            if bonus.alive and player.hitbox.colliderect(bonus.hitbox):
                bonus.alive = False
                self.score += 200
            
            for le in lower_landscape:
                le.draw()

            # Draw upper landscape above lower landscape
            for le in upper_landscape:
                le.draw()

            bonus.draw()
            
            player.draw()
            
            for obs in obstacles:
                obs.draw()
            
            
            # Spawn Lanscape elements, Obstacles and Bonuses
            if random.random() < 0.01:
                for le in lower_landscape:
                    if not le.alive:
                        le.spawn(random.choice(bush_sprites + rock_sprites + wood_sprites))
                        break
            if random.random() < 0.01:
                for le in upper_landscape:
                    if not le.alive:
                        le.spawn(random.choice(tree_sprites))
                        break
            
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
            
            current_time=time.time() - self.time0
            
            #####################
            ######## HUD ########
            #####################

            self.draw_text(self.get_banner(), 25, self.size_x/2, 1)
            
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.menu()
       
