import pygame as pg
import random
import threading
import time
from game_entities import Player, SideObstacle, Bonus

from mqtt_subscriber import mqtt_subscriber

_DEBUG=True
class Console():
    """ Class Console to manage the game
        using a single input rot_speed
        It provides a method get_speed to be called outside
        of the class to read a 'sensor value'
    """
    def __init__(self):
        """ Class constructor """
        # Screen configuration
        self.size_x=480
        self.size_y=640
        self.dir_img='images'
        # Max speed 
        self.ROT_SPEED_MAX = 700
        # rot speed max = 700, screen speed max = 3 => 3/600
        self.SPEED_RATIO=0.005
        # Control variable
        self.jump=0
        self._on_message = None
        # raw speed value received from the mqtt sensor
        self.rot_speed=0
        # speed = SPEED_RATIO*rot_speed = speed of the screen
        self.speed=0
        self.energy=0.0
        self.score=0
        # initial time when the game begins
        self.time0=0
        # Screen init
        pg.init()
        self.screen = pg.display.set_mode((self.size_x, self.size_y))
        pg.display.set_caption('Fit&Fun')
        # Font, Colors
        self.font_name = pg.font.match_font('arial')
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        # lock for synchro to kill the sensor speed client
        self.synchro = threading.Lock()

    def menu(self):
        """ First ntry panel before launching the game"""
        # Load and display the image menu
        image=pg.image.load(self.dir_img+'/menu.png')
        image=pg.transform.scale(image, (640,480))
        # You enter in the new panel game when you click 
        # on the arrow of the image located in (300,320)
        while True:
            self.screen.blit(image,(0,0))
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.display.quit()
                    exit() 
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.pos[0] in range(300,320) and event.pos[1] in range(200,220) :
                        self.game()

    def _draw_text(self, text, size, x, y):
        """ Print text on the panel with 

         Parameters
        ----------
            size: int
                size of the text
            x: int
                x location of the text
            y: int
                y location of the text
        """
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.BLACK)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def game(self):
        """
        game panel. A character go headed on a scrolled side game depending
        on its speed. If it reaches muschroom the score is decrease.
        """
        # Time init
        clock = pg.time.Clock()
        self.time0=time.time()

        # Sprite assets loading
        desert_bg = pg.image.load(self.dir_img+'/desert.jpg')
        bg_size = desert_bg.get_size()
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
            self.screen.blit(desert_bg,(0, bg_y - bg_size[1]))
            self.screen.blit(desert_bg,(0, bg_y))
            self.screen.blit(desert_bg,(0, bg_y + bg_size[1]))
            bg_y = bg_y + bg_scroll_speed
            if bg_y >= bg_size[1]:
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

            self._draw_text(self.get_banner(), 25, self.size_x/2, 1)
            
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.display.quit()
                    print("QUIT")
                    self.synchro.release()
                    exit() 
       

    def get_banner(self):
        """ Format textual information
        
            Return
            ------
            banner: string
             contains time, speed and score
        """
        duration=time.time() - self.time0
        minutes, seconds = divmod(duration, 60)
        template = "Time: {min:02d}:{sec:02d} - Speed: {speed:03d} - Score: {score:03d}"
        banner= template.format(min=int(minutes), sec=int(seconds), 
                            speed=int(self.rot_speed), score=self.score+int(self.energy))
        return banner

    def get_speed(self, client, userdata, message):
        """ extract and normalize the rotation raw speed
            compatible (client/userdata) with a mqtt subscriber
            callback

            Parameters
            ----------
                size: string
                    speed rotation (0 to 700)
        """
        try:
            rot_speed=float(str(message.payload.decode("utf-8"))) 
            if rot_speed < self.ROT_SPEED_MIN:
                self.rot_speed=0
                self.speed=0
            else:
                self.rot_speed=rot_speed
                self.speed=round(self.SPEED_RATIO*self.rot_speed)
        except Exception:
            self.speed=0
            self.rot_speed=0

        #self.score=self.score+self.speed
        if self.speed > 2:
            self.jump=1
        else:
            self.jump=0

        if _DEBUG==True: print(self.get_banner())


# Main
if __name__ == "__main__":
    console=Console()
    mqtt_sub=mqtt_subscriber(console.get_speed, console.synchro, 'fit_and_fun/speed')
    mqtt_sub.run()
    console.game()
