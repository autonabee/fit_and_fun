import pygame as pg
import time
import random
from console import Console
from game_entities import Player, SideObstacle, Bonus


class GameCanoe(Console):

    def __init__(self):
        super().__init__()
    
    def game(self):
        """
        game panel. A character go headed on a scrolled side game depending
        on its speed. If it reaches muschroom the score is decrease.
        """
        # Time init
        clock = pg.time.Clock()
        self.time0=time.time()

        # Sprite assets loading
        river_bg = pg.image.load(self.dir_img+'/river.png')
        river_bg = pg.transform.scale(river_bg, (self.size_x, self.size_y))
        mushroom_sprite = pg.image.load(self.dir_img + "/mushroom.png")
        player = Player(self.screen, self.dir_img + "/boy.png")
        
        # Data
        last_speed = 0  # Used for value smoothing
        bg_y = 0
        bg_scroll_speed = 1.5
        
        # Create permanent obstacles entities
        obstacles = [SideObstacle(self.screen) for _ in range(3)]
        bonus = Bonus(self.screen)
        bonus.spawn(300)

        while True:
            delta = clock.tick(30)
            
            # Background scrolling
            self.screen.blit(river_bg,(0, bg_y - self.size_y))
            self.screen.blit(river_bg,(0, bg_y))
            self.screen.blit(river_bg,(0, bg_y + self.size_y))
            bg_y = bg_y + bg_scroll_speed
            if bg_y >= self.size_y:
                bg_y=0
            
            # Normalizing and smoothing
            speed =  0.8 * last_speed + 0.2 * (self.rot_speed / self.ROT_SPEED_MAX)
            last_speed = speed
            # Speed should be normalized    
            player.speed = speed    
            player.update(delta)
            
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
            
            bonus.draw()
            
            player.draw()
            
            for obs in obstacles:
                obs.draw()
            
            
            # Spawn Obstacles and Bonuses
            if random.random() < 0.02:
                for obs in obstacles:
                    if not obs.alive:
                        side = 1
                        if random.random() < 0.5:
                            side = -1
                        
                        obstacle_height = random.random() * self.size_y
                        obs.spawn(mushroom_sprite, obstacle_height, side)
                        break
            
            if not bonus.alive and random.random() < 0.002:
                bonus.spawn(random.random() * self.size_y)
            
            
            #####################
            ######## HUD ########
            #####################

            self.draw_text(self.get_banner(), 25, self.size_x/2, 1)
            
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    self.synchro.release()
                    exit() 
       
