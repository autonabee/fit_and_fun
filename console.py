import pygame as pg
import pygame_menu as pg_menu
from pygame_menu import themes, Theme

import threading
import time

# Custom menu theme

mytheme = pg_menu.themes.THEME_BLUE.copy()
myimage = pg_menu.baseimage.BaseImage(
    image_path="images/desert.jpg",
    drawing_mode=pg_menu.baseimage.IMAGE_MODE_REPEAT_XY
)
mytheme.background_color = myimage
mytheme.widget_font=pg_menu.font.FONT_NEVIS

class Console():
    """ Class Console to manage the game
        using a single input rot_speed
        It provides a method get_speed to be called outside
        of the class to read a 'sensor value'
    """
    dir_img='images'

    def __init__(self, wind=None):
        """ Class constructor """
        # Screen configuration
        self.size_x=480
        self.size_y=640
        # Min/Max speed 
        self.ROT_SPEED_MIN = 00
        self.ROT_SPEED_MAX = 15
        # rot speed max = 700, screen speed max = 3 => 3/600
        self.SPEED_RATIO=0.005 
        # 2*Pi rad (1 revolution) -> 0.5 meter
        self.DIST_RATIO=0.079577472
        # Control variable
        self._on_message = None
        # raw speed value (rad/s) received from the mqtt sensor
        self.rot_speed=0
        # speed = SPEED_RATIO*rot_speed = speed of the screen (no unit )
        self.speed=0
        # distance in meter = DIST_RATIO*rot_speed*dt
        self.distance=0.0
        self.mean_rot_speed=0.0
        self.score=0
        # initial time when the game begins
        self.time0=0
        # current time
        self.time=0
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
        self.difficulty=1
        self.name='Julien'
        # Wind resistor
        self.wind_resistor = wind

    def set_wind(self):
        """ Activate the wind if the object exists"""
        if self.wind_resistor != None:
            self.wind_resistor.activate()

    def set_level(self, value, difficulty):
        """ callback called by self.levelmenu """
        self.difficulty=difficulty
   
    def set_user(self, selec_name, name): 
        """ callback called by self.usermenu """
        self.name=name
   
    def level_menu(self): 
        """ Open self.levelmenu """
        self.mainmenu._open(self.levelmenu)
 
    def user_menu(self):
        """ Open self.usermenu """
        self.mainmenu._open(self.usermenu)
 
    def menu(self):
        """ Menu game management """
        # Main entry menu
        self.mainmenu = pg_menu.Menu('FIT and FUN', self.size_x, self.size_y, theme=mytheme)
        # User name 
        self.mainmenu.add.button('User', self.user_menu)
        self.usermenu = pg_menu.Menu('Select a User', self.size_x, self.size_y, theme=mytheme)
        self.usermenu.add.selector('Name :', [('Julien', 'Julien'), ('Christophe', 'Christophe')], onchange=self.set_user)
        # Launch the game
        self.mainmenu.add.button('Play', self.game)
        # Select the level of the game
        self.mainmenu.add.button('Levels', self.level_menu)
        self.levelmenu = pg_menu.Menu('Select a Level', self.size_x, self.size_y, theme=mytheme)
        self.levelmenu.add.selector('Level :', [('Non-regular', 1), ('Regular', 2)], onchange=self.set_level)
        # Quit the game
        self.mainmenu.add.button('Quit', pg_menu.events.EXIT)
        # Event loop
        while True:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT: 
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    self.synchro.release() 
                    if self.wind_resistor != None:
                        self.wind_resistor.stop()
                    exit()
        
            if self.mainmenu.is_enabled():
                self.mainmenu.update(events)
                self.mainmenu.draw(self.screen)
            pg.display.update()
   

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
                            speed=int(self.rot_speed), score=self.score+int(self.distance))
        return banner

    def reset_data(self):
        self.time0=time.time()
        self.distance=0
        self.mean_rot_speed=0

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
            rot_speed=abs(rot_speed)
            # ro_speed normalisation
            if rot_speed < self.ROT_SPEED_MIN:
                self.rot_speed=0
                self.speed=0
            elif rot_speed > self.ROT_SPEED_MAX:
                self.rot_speed=self.ROT_SPEED_MAX
            else:
                self.rot_speed=rot_speed
            # speed update
            self.speed=round(self.SPEED_RATIO*self.rot_speed)
            # compute deltatime dt and update data values
            current_time = time.time()
            dt=0
            if self.time == 0:
                self.distance=0
            else:
                dt = current_time - self.time
                self.distance+=(self.rot_speed*self.DIST_RATIO*dt)
                self.mean_rot_speed=self.distance/((current_time - self.time0)*self.DIST_RATIO)
            self.time=current_time
        except Exception:
            self.speed=0
            self.rot_speed=0

        #self.score=self.score+self.speed
        if self.debug==True: print(self.get_banner())
