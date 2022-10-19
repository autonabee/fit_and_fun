import pygame as pg
import threading
import time

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
        # Min/Max speed 
        self.ROT_SPEED_MIN = 10
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
        self.debug=True

    def menu(self):
        """ First entry panel before launching the game"""
        # Load and display the image menu
        image=pg.image.load(self.dir_img+'/menu.png')
        image=pg.transform.scale(image, (self.size_x, self.size_y))
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
                    if event.pos[0] in range(230,240) and event.pos[1] in range(280,295) :
                        self.game()

    def draw_text(self, text, size, x, y):
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

        if self.debug==True: print(self.get_banner())
