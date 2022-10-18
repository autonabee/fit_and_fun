import pygame as pg
import random
import threading
import time

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
        self.size_x=640
        self.size_y=480
        self.dir_img='images'
        # Minimun speed
        self.ROT_SPEED_MIN=10
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
        game panel. A little guy go headed on a scrolled side game if
        the speed is > 0 and go higher if the speed > 2. If it reaches
        muschroom the score is increasing.
        """
        # Image of the background landscape
        image=pg.image.load(self.dir_img+'/level1.png')
        image=pg.transform.scale(image, (640,480))
        bgx=0
        # The little guy
        player=pg.image.load(self.dir_img+'/boy.png')
        player=pg.transform.rotozoom(player,0,0.2)
        player_y = 325
        # The mushroom
        mushroom=pg.image.load(self.dir_img+'/mushroom.png')
        mushroom=pg.transform.rotozoom(mushroom,0,0.8)
        # The crate
        crate=pg.image.load(self.dir_img+'/crate.png')
        crate=pg.transform.rotozoom(crate,0,0.5)
        # Target (mushroom:0 or crate:1) position
        target_x=700
        target_speed=2
        target_type=1
        # Initial time recorded
        self.time0=time.time()
        # Game behavior
        while True:
            # Background landscape advances with bgx
            # so the little guy seems to advance
            self.screen.blit(image,(bgx-640,0))
            self.screen.blit(image,(bgx,0))
            self.screen.blit(image,(bgx+640,0))
            bgx = bgx - self.speed
            if bgx <= -640:
                bgx=0
            # The litte guy can go higher with player_y if
            # a 'jump' is required
            p_rect=self.screen.blit(player,(50, player_y))
            player_y=325-50*self.jump    
            # Mushroom advances with mushroom_x
            # when it disapear we create another one randomly
            if target_type == 0:
                c_rect=self.screen.blit(mushroom,(target_x,250))
            else:
                c_rect=self.screen.blit(crate,(target_x,250))
            target_x -= target_speed
            if target_x < -50:
                target_x=random.randint(800,1000)
                target_speed=random.randint(2,3)
                target_type=random.randint(0,1)
            # Detect the collision between the target and the little guy
            # score+ if it is a mushroom, score- if it is a crate
            if p_rect.colliderect(c_rect):
                if target_type==0:
                    self.score+=10
                else:
                    self.score-=10
                target_x=-51
            self.energy+=self.speed/1000.0 
            # Draw a banner with textual information
            self._draw_text(self.get_banner(), 30, 320, 1)
            # Loop event
            pg.display.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if _DEBUG==True: print("Quit") 
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
    console.menu()
