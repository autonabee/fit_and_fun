import pygame as pg
import random
import os
from console import Console


class Player():
    sprites_path = ["canoe_1.png", "canoe_2.png"]
    pos_y = 0
    hit_cooldown = 0
    cooldown_counter = 0
    speed = 0   # Speed should be a normalized value between 0 and 1
    
    def __init__(self, screen):
        self.screen = screen
        self.sprites = [pg.image.load(os.path.join(Console.dir_img, filename)) for filename in self.sprites_path]
        self.width = self.sprites[0].get_width()
        self.height = self.sprites[0].get_height()
        self.pos_x = (self.screen.get_width() - self.width) * 0.5
        self.sprite_idx = 0
        self.anim_counter = 0

    
    def update(self, delta):
        assert 0 <= self.speed <= 1, "speed value is outside [0,1] range"
        self.pos_y = self.screen.get_height() - self.height \
                    - self.speed * (self.screen.get_height() - self.height)
        self.hitbox = pg.Rect(self.pos_x + 55, self.pos_y + 2, self.width - 110, self.height - 4)
        if self.hit_cooldown > 0:
            self.hit_cooldown -= delta
        
        self.anim_counter += 1
        if self.anim_counter >= 6:
            self.anim_counter = 0
            self.sprite_idx = (self.sprite_idx + 1) % 2
    
    def draw(self):
        if self.hit_cooldown > 0:
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
            self.hit_cooldown = 3000
            return True
        return False



class LandscapeProp():
    
    def __init__(self, screen):
        self.screen = screen
        self.alive = False
    
    def spawn(self, sprite):
        self.alive = True
        self.sprite = sprite
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        if random.random() < 0.5:
            # Spawn left of the river
            self.pos_x = 30 + random.randint(-24, 24)
        else:
            # Or spawn right of the river
            self.pos_x = self.screen.get_width() - 30 + random.randint(-10, 10)
        self.pos_y = -self.height * 0.5
    
    def update(self, delta, bg_speed):
        if not self.alive:
            return
        
        self.pos_y += delta * bg_speed
        if self.pos_y < -self.height or self.pos_y > self.screen.get_height() + self.height:
            self.alive = False
    
    def draw(self):
        if self.alive:
            self.screen.blit(self.sprite, (self.pos_x - 0.5*self.width, self.pos_y - 0.5*self.height))
    


class Obstacle():
    collision_margin = 2
    
    def __init__(self, screen):
        self.screen = screen
        self.alive = False
    
    
    def spawn(self, sprite, height, side=1, speed=0.1):
        self.alive = True
        self.sprite = sprite
        self.size = self.sprite.get_size()
        self.side = side
        self.speed = speed
        self.pos_y = height
        
        if side == 1:
            self.pos_x = -self.size[0] * 0.5
        else:
            self.pos_x = self.screen.get_width() + self.size[0] * 0.5
    
    
    def update(self, delta):
        if not self.alive:
            return

        self.pos_x += self.side * self.speed * delta
        self.hitbox = pg.Rect(self.pos_x - 0.5*self.size[0] + self.collision_margin,
                                     self.pos_y - 0.5*self.size[1] + self.collision_margin,
                                     self.size[0] - 2 * self.collision_margin,
                                     self.size[1] - 2 * self.collision_margin)
            
        # Kill obstacle when out of screen
        if self.pos_x > self.screen.get_width() + self.size[0] or self.pos_x < -self.size[0]:
            self.alive = False
    
    
    def draw(self):
        if self.alive:
            self.screen.blit(self.sprite, (self.pos_x - 0.5*self.size[0], self.pos_y - 0.5*self.size[1]))
            # Hitbox debug drawing
            #pg.draw.rect(self.screen, (0, 255, 0), self.hitbox)



class Bonus():
    sprites_path = ["tremplin_0.png", "tremplin_1.png"]

    def __init__(self, screen):
        self.screen = screen
        self.alive = False
        self.sprites = [pg.image.load(os.path.join(Console.dir_img, filename)) for filename in self.sprites_path]
        self.width = self.sprites[0].get_width()
        self.height = self.sprites[0].get_height()


    def spawn(self, height):
        self.alive = True
        # self.sprite = sprite
        # self.size = self.sprite.get_size()
        self.pos_y = height
        self.lifetime = 5000
        self.counter = 0
        center = self.screen.get_width() * 0.5
        self.hitbox = pg.Rect(center-25, self.pos_y-self.height*0.5, 50, self.height)


    def update(self, delta):
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
