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


import pygame as pg
import random
import os



class Player():
    SPRITES_PATH = ["canoe_1.png", "canoe_2.png"]
    ROWING_ANIM_SPEED_MAX = 0.2    # Don't go above 1.0 ! define paddle stroke speed 
    HIT_BLINK_DURATION = 3.0        # Blinking period duration after being hit (in seconds)
    

    def __init__(self, screen, dir_img):
        self.screen = screen
        self.sprites = [pg.image.load(os.path.join(dir_img, filename)) for filename in self.SPRITES_PATH]
        self.width = self.sprites[0].get_width()
        self.height = self.sprites[0].get_height()
        self.pos_x = (self.screen.get_width() - self.width) * 0.5 # player position on the middle of the screen
        self.pos_y = 0 # player position on the bottom of the screen
        self.hitbox = pg.Rect(self.pos_x + 55, self.pos_y + 8, self.width - 110, self.height - 20)
        self.sprite_idx = 0
        self.anim_counter = 0.0
        self.hit_cooldown = 0.0
        self.cooldown_counter = 0.0
        self.speed = 0.0   # Speed should be a normalized value between 0 and 1

    
    def update(self, delta):
        """ Update the state of the element
            should be called every frame

            Parameters
            ----------
                delta: float
                    elapsed time since last frame (in milliseconds)
        """

        assert 0 <= self.speed <= 1, "speed value is outside [0,1] range"

        screen_height = self.screen.get_height()
        ##self.pos_y = screen_height/2
        ##self.pos_y = screen_height - self.height \
              ##     - self.speed * (screen_height - self.height)        
       ## self.pos_y = 0.9 * self.pos_y + 0.05 * screen_height  # Up and bottom margin
        
        self.hitbox.x = self.pos_x + 55
        self.hitbox.y = self.pos_y + 10
        
        if self.hit_cooldown > 0:
            self.hit_cooldown -= delta
        
        # Rowing animation speed depends of player speed
        self.anim_counter += self.ROWING_ANIM_SPEED_MAX * self.speed
        if self.anim_counter >= 1:
            self.anim_counter = 0
            self.sprite_idx = (self.sprite_idx + 1) % 2
    

    def draw(self):
        if self.hit_cooldown > 0:
            # Blink for a while after being hit
            self.cooldown_counter += 1
            if (self.cooldown_counter // 4) % 2 == 0:
                self.screen.blit(self.sprites[self.sprite_idx], (self.pos_x, self.pos_y))
        else:
            self.screen.blit(self.sprites[self.sprite_idx], (self.pos_x, self.pos_y))
        # Hitbox debug drawing
        #pg.draw.rect(self.screen, (0, 255,0), self.hitbox)
    

    def hit(self):
        """ returns True if the hit was effective, False otherwise """
        if self.hit_cooldown <= 0:
            self.hit_cooldown = self.HIT_BLINK_DURATION * 1000
            return True
        return False



class LandscapeProp():
    """ Landscape element
        Simply decorative, they doesn't interact with the player
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.alive = False
        self.layer = 0
    

    def spawn(self, sprite, layer=0):
        """ Spawn a new landscape element

            Parameters
            ----------
                sprite: pygame.Surface
                layer: int
                    drawing layer (higher numbers will be drawn on top)
        """
        self.alive = True
        self.layer = layer      # Drawing layer, higher numbers will be drawn on top of lower numbers
        self.sprite = sprite
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        if random.random() < 0.5:
            # Spawn left of the river
            self.pos_x = 40 + random.randint(-50, 50)
        else:
            # Or spawn right of the river
            self.pos_x = self.screen.get_width() - 40 + random.randint(-50, 50)
        self.pos_y = -self.height * 0.5
    

    def update(self, delta, scroll_speed):
        """ Update the state of the element
            should be called every frame

            Parameters
            ----------
                delta: float
                    elapsed time since last frame (in milliseconds)
                scroll_speed: float
                    scrolling speed
        """
                
        if not self.alive:
            return
        
        self.pos_y += delta * scroll_speed
        if self.pos_y < -self.height or self.pos_y > self.screen.get_height() + self.height:
            self.alive = False
    
    
    def draw(self):
        if self.alive:
            self.screen.blit(self.sprite, (self.pos_x - self.width/2, self.pos_y - self.height/2))
    


class Obstacle():
    """ An obstacle coming from the left or the right
        Can collide with the player
    """

    COLLISION_MARGIN = 2
    

    def __init__(self, screen):
        self.screen = screen
        self.alive = False
    
    
    def spawn(self, sprite, height, side=1, speed=1.0):
        self.alive = True
        self.sprite = sprite
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.side = side
        self.speed = speed * 0.1
        self.pos_y = height
        
        if side == 1:
            self.pos_x = -self.width * 0.5
        else:
            self.pos_x = self.screen.get_width() + self.width * 0.5
        
        self.hitbox = pg.Rect(self.pos_x - 0.5 * self.width + self.COLLISION_MARGIN,
                                     self.pos_y - 0.5 * self.height + self.COLLISION_MARGIN,
                                     self.width - 2 * self.COLLISION_MARGIN,
                                     self.height - 2 * self.COLLISION_MARGIN)
    
    
    def update(self, delta):
        """ Update the state of the element
            should be called every frame

            Parameters
            ----------
                delta: float
                    elapsed time since last frame (in milliseconds)
        """

        if not self.alive:
            return

        self.pos_x += self.side * self.speed * delta
        self.hitbox.x = self.pos_x - 0.5 * self.width + self.COLLISION_MARGIN
            
        # Disable obstacle when out of screen
        if self.pos_x > self.screen.get_width() + self.width or self.pos_x < -self.width:
            self.alive = False
    
    
    def draw(self):
        if self.alive:
            self.screen.blit(self.sprite, (self.pos_x - 0.5 * self.width, self.pos_y - 0.5 * self.height))
            # Hitbox debug drawing
            #pg.draw.rect(self.screen, (0, 255, 0), self.hitbox)



class Bonus():
    """ A bonus element that the player should catch
        Spawned on the river, can collide with the player
    """

    SPRITES_PATH = ["tremplin_0.png", "tremplin_1.png"]
    LIFETIME = 5.0  # Lifetime of the bonus (in seconds)

    def __init__(self, screen, dir_img):
        self.screen = screen
        self.alive = False
        self.sprites = [pg.image.load(os.path.join(dir_img, filename)) for filename in self.SPRITES_PATH]
        self.width = self.sprites[0].get_width()
        self.height = self.sprites[0].get_height()
        self.lifetime = 0


    def spawn(self, height):
        self.alive = True
        # self.sprite = sprite
        # self.size = self.sprite.get_size()
        self.pos_y = height
        self.lifetime = self.LIFETIME * 1000
        self.counter = 0
        center = self.screen.get_width() * 0.5
        self.hitbox = pg.Rect(center-25, self.pos_y - self.height*0.5, 50, self.height)


    def update(self, delta):
        """ Update the state of the element
            should be called every frame

            Parameters
            ----------
                delta: float
                    elapsed time since last frame (in milliseconds)
        """
        if not self.alive:
            return
        
        self.lifetime -= delta
        if self.lifetime <= 0:
            self.alive = False


    def draw(self):
        if not self.alive:
            return
        
        center = self.screen.get_width() * 0.5

        self.counter += 1
        sprite = self.sprites[(self.counter // 6) % 2]
        
        self.screen.blit(sprite, (center - self.width * 0.5, self.pos_y - self.height * 0.5))
        
        # Hitbox debug drawing
        #pg.draw.rect(self.screen, (0,255,0), self.hitbox)
