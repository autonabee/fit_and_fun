import pygame as pg
import pygame_menu as pg_menu
from pygame_menu import themes, Theme, widgets
from functools import partial
import database as db
import pygame_vkeyboard as vkboard


import threading
import time
import os
import sys

# Custom menu theme

mytheme = pg_menu.themes.THEME_DEFAULT.copy()
myimage = pg_menu.baseimage.BaseImage(
    image_path=os.path.join(os.path.dirname(__file__),"images/menu_bg.png"),
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
    
    dir_img=os.path.join(os.path.dirname(__file__), 'images')

    #Images
    heart_full_img = pg.image.load(dir_img+'/heart_full.png')
    heart_empty_img = pg.image.load(dir_img+'/heart_empty.png')

    clock = pg.time.Clock()
    
    def __init__(self, wind=None, debug=False, fullscreen=False, timer=120):
        """ Class constructor """
        # Min/Max speed 
        self.ROT_SPEED_MIN = 00
        self.ROT_SPEED_MAX = 15
        # rot speed max = 700, screen speed max = 3 => 3/600
        # Ratio between effective speed and apparent score
        self.SCORE_RATIO=0.02
        # Control variable
        self._on_message = None
        # raw speed value received from the mqtt sensor
        self.rot_speed=0
        self.speed=0.0
        self.energy=0.0
        self.score=0
        # initial time when the game begins
        self.time0=0
        # initial time when the boat pass the GO line
        self.timebegin=0
        # Screen init
        pg.init()
        if fullscreen:
            self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
            self.size_x = self.screen.get_width()
            self.size_y = self.screen.get_height()
        else:
            self.size_x = 600
            self.size_y = 1024
            self.screen = pg.display.set_mode((self.size_x, self.size_y))
        pg.display.set_caption('Fit&Fun')
        #Add a delay before you can press a key again
        pg.key.set_repeat(150)
        # Font, Colors
        self.font_name = pg.font.match_font('arial')
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        # lock for synchro to kill the sensor speed client
        self.synchro = threading.Lock()
        self.debug=debug
        self.difficulty=1
        self.timer=timer #Allowed time in seconds
        self.name='Julien'
        # Wind resistor
        self.wind_resistor = wind

    def set_wind(self):
        """ Activate the wind if the object exists"""
        if self.wind_resistor != None:
            self.wind_resistor.activate()
   
    def set_user(self, username, name): 
        """ callback called by self.usermenu """
        self.name=name
 
    def display_select_user_ui(self):
        self.name = 'Invite'
        list_users = [('Invite','Invite'), ('Julien','Julien'), ('Christophe','Christophe')]

        #db.obtain_users_list()

        select_user_ui = pg_menu.Menu('SELECTIONNEZ UN JOUEUR', self.size_x, self.size_y, theme=mytheme)
        select_user_ui.add.dropselect('UTILISATEUR :', list_users, default = 0, onchange=self.set_user)
        select_user_ui.add.button('VALIDER', self.display_select_game_ui)
        select_user_ui.add.button('NOUVEAU JOUEUR', self.display_create_user_ui)
        select_user_ui.add.button('HISTORIQUE', self.display_history_ui)
        select_user_ui.add.button('QUITTER', pg_menu.events.EXIT)
        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    self.synchro.release()

            select_user_ui.update(events)

            select_user_ui.draw(self.screen)
            pg.display.update()


    def set_game(self, game_name, game):
        self.game = game


    def display_select_game_ui(self):
        select_game_ui = pg_menu.Menu('SELECTIONNEZ UN JEU', self.size_x, self.size_y, theme=mytheme)
        select_game_ui.add.selector('', [('ducks', 'ducks')], onchange=self.set_game)
        select_game_ui.add.button('VALIDER', self.display_select_exercise_ui)
        select_game_ui.add.button('STATISTIQUES', self.display_stats_ui)
        select_game_ui.add.button('CHANGER DE JOUEUR', self.display_select_user_ui)
        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit")
                    self.synchro.release()

            select_game_ui.update(events)

            select_game_ui.draw(self.screen)
            pg.display.update()


    def set_exercise(self, exercise_display, exercise_value):
        self.exercise = exercise_value

    def display_define_exercise_ui(self):
        print("Création d'un exercice")
        return
    
    def display_select_exercise_ui(self):#TODO
        self.exercise = ('Echauffement','Echauffement')
        list_exercise = [('Echauffement','Echauffement'), ('Paliers simples','Paliers simples'), ('Pyramide','Pyramide')]
        
        ##import from the database

        select_exercise_ui = pg_menu.Menu('SELECTIONNEZ UN EXERCICE', self.size_x, self.size_y, theme=mytheme)
        select_exercise_ui.add.dropselect('EXERCICE :', list_exercise, default = 0, onchange=self.set_exercise)
        select_exercise_ui.add.button('JOUER', self.set_parameters)
        select_exercise_ui.add.button('MODIFIER EXERCICE', self.display_modify_exercise_ui) #passer en param l'exercice à modifier, peut etre un booleen si c'est modif ou nouveau is_new?? + prévoir si dropselect est vide
        select_exercise_ui.add.button('NOUVEL EXERCICE', self.display_define_exercise_ui)
        select_exercise_ui.add.button('CHANGER DE JEU', self.display_select_game_ui)
        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    self.synchro.release()

            select_exercise_ui.update(events)

            select_exercise_ui.draw(self.screen)
            pg.display.update()

    

################ partie création d'un exercice, ne fonctionne pas
    # def set_exercice(self, value):
    #     self.nbseries=value


    # def set_exercice_name(self, name):
    #     self.name_exercice=name


    # def display_define_exercise_ui(self):
    #     select_define_exercise = pg_menu.Menu('DEFINISSEZ UN EXERCICE', self.size_x, self.size_y, theme=mytheme)
    #     select_define_exercise.add.textinput("Nom De l'exercice", input_type=str,onchange=self.set_exercise_name())
    #     select_define_exercise.add.textinput('Nombre de séries', input_type=int,onchange=self.set_exercise())
    #     select_define_exercise.add.button('Paramètrer', self.display_define_series_ui)
       
    #     while True:
    #         time_delta = self.clock.tick(60)/1000.0
    #         events = pg.event.get()


    #         for event in events:
    #             if event.type == pg.QUIT:
    #                 pg.display.quit()
    #                 if self.debug : print("Quit")
    #                 self.synchro.release()


    #         select_define_exercise.update(events)


    #         select_define_exercise.draw(self.screen)
    #         pg.display.update()

    
   
    # def set_series(self, value, i, j):
    #     self.table[i][j] = value


    # def display_define_series_ui(self):
    #     select_define_series = pg_menu.Menu('PARAMETREZ LES SERIES', self.size_x, self.size_y, theme=mytheme)


    #     for i in range (0,self.nbseries):
    #         select_define_series.add.textinput('Durée (s)', input_type=int,onchange=self.set_series(i, 0))
    #         select_define_series.add.textinput('Vitesse', input_type=int,onchange=self.set_series(i, 1))
    #         select_define_series.add.textinput('Force', input_type=int,onchange=self.set_series(i, 2))

   
    #     select_define_series.add.button('VALIDER', self.display_select_exercise_ui)
   
    #     while True:
    #         time_delta = self.clock.tick(60)/1000.0
    #         events = pg.event.get()


    #         for event in events:
    #             if event.type == pg.QUIT:
    #                 pg.display.quit()
    #                 if self.debug : print("Quit")
    #                 self.synchro.release()

    #         select_define_series.update(events)

    #         select_define_series.draw(self.screen)
    #         pg.display.update()


    def display_modify_exercise_ui(self): #sur le meme modele que precedemment
        print('Displays the options to modify the exercise selected on the dropselect widget')
        return


    def set_parameters(self):#TODO
        print("set game parameters according to the selected exercise before launching the game")
        self.game()
    



    def display_history_ui(self):#TODO
        history_ui = pg_menu.Menu('HISTORIQUE', self.size_x, self.size_y, theme=mytheme)
        #recherche des dernieres parties dans bdd
        #db.general_history()
        #bouton -> : accès au 10 parties précédentes
        #bouton <- : accès au 10 parties suivantes
        history_ui.add.button('RETOUR', self.display_select_user_ui)

        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    self.synchro.release()

            history_ui.update(events)

            history_ui.draw(self.screen)
            pg.display.update()



    def display_stats_ui(self):#TODO faire le lien avec la BDD
        stats_ui = pg_menu.Menu('STATISTIQUES', self.size_x, self.size_y, theme=mytheme)
        #bdd
        stats_ui.add.button('RETOUR', self.display_select_game_ui)

        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    self.synchro.release()

            stats_ui.update(events)

            stats_ui.draw(self.screen)
            pg.display.update()
    


    def display_delete_user_ui(self): #TODO
        print('Displays delet user ui')
        return
    
    def on_key_event(self, text):
        print(text)
        
    def display_create_user_ui(self): #TODO

        create_user_ui = pg_menu.Menu('NEW USER', self.size_x, self.size_y, theme=mytheme)
        create_user_ui.add.button('VALIDER')#fonction à créer, rajouter entrée dans db
        create_user_ui.add.button('RETOUR', self.display_select_user_ui)
        
        layout = vkboard.VKeyboardLayout(vkboard.VKeyboardLayout.AZERTY)
        keyboard = vkboard.VKeyboard(create_user_ui,
                                    self.on_key_event,
                                    layout,
                                    renderer=vkboard.VKeyboardRenderer.DARK,
                                    show_text=False)
        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug: print("Quit") 
                    self.synchro.release()

            create_user_ui.update(events)
            keyboard.update(events)
            create_user_ui.draw(self.screen)
            rects = keyboard.draw(self.screen)

            # Flip only the updated area
            pg.display.update(rects)

    
 
    def display_score_ui(self, duration, distance):
        """ Open self.score_ui """
        self.score_ui = pg_menu.Menu('FELICITATIONS!', self.size_x, self.size_y, theme=mytheme)
        minutes, seconds = divmod(duration, 60)
        self.score_ui.add.label("Time : " + str(int(minutes)) + "'" + str(int(seconds)) + "\"")
        self.score_ui.add.label("Distance : " + str(round(distance)))
        self.score_ui.add.label("Score : " + str(round(self.score)))
        self.score_ui.add.button('REJOUER', self.game)
        self.score_ui.add.button('MENU', partial(self.display_select_game_ui))
        self.score_ui.add.button('QUITTER', pg_menu.events.EXIT)
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

            if self.score_ui.is_enabled():
                self.score_ui.update(events)
                self.score_ui.draw(self.screen)
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

    def draw_life(self, life_count):
        """ Print life counter in the top left corner with 

         Parameters
        ----------
            life_counter: int
                number of remaining lives
        """
        self.screen.blit(self.heart_full_img, (5, 30))
        if(life_count >= 2):
            self.screen.blit(self.heart_full_img, (5, 61))
        else:
            self.screen.blit(self.heart_empty_img, (5, 61))
        if(life_count == 3):
            self.screen.blit(self.heart_full_img, (5, 92))
        else:
            self.screen.blit(self.heart_empty_img, (5, 92))

    def get_banner(self):
        """ Format textual information
        
            Return
            ------
            banner: string
             contains time, speed and score
        """
        #Timer activates only when the game begins
        if self.timebegin == 0 :
            minutes, seconds = divmod(self.timer, 60)
        else:
            duration = time.time() - self.timebegin
            minutes, seconds = divmod(self.timer - duration, 60)
        template = "Time: {min:02d}:{sec:02d} - Speed: {speed:03d} - Score: {score:03d}"
        banner = template.format(min=int(minutes), sec=int(seconds), 
                            speed=int(self.rot_speed), score=round(self.score)+int(self.energy))
        return banner

    def message_callback(self, client, userdata, message):
        """ executes the function corresponding to the called topic
        """
        if message.topic == "fit_and_fun/speed":
            self.get_speed(client, userdata, message)
        elif message.topic == "fit_and_fun/select":
            self.btn_select(client, userdata, message)
        elif message.topic == "fit_and_fun/down":
            self.btn_down(client, userdata, message)
        else:
            print("WARNING: topic " + message.topic + " unknown\n")


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
            if rot_speed < self.ROT_SPEED_MIN:
                self.rot_speed=0
                self.speed=0.0
            elif rot_speed > self.ROT_SPEED_MAX:
                self.rot_speed=self.ROT_SPEED_MAX
            else:
                self.rot_speed=rot_speed
            self.speed=self.SCORE_RATIO*self.rot_speed
        except Exception:
            self.speed=0.0
            self.rot_speed=0

        self.score=self.score+self.speed

        if self.debug==True: print(self.get_banner())

    #Different input types to simulate
    INPUT_SELECT = 0
    INPUT_DOWN = 1
    INPUT_BACK = 2
    INPUT_ESC = 3

    def simulate_input(self, input_type: int):
        if input_type == self.INPUT_SELECT:
            #Simulate a keyboard 'return' ('enter' key) input
            newevent = pg.event.Event(pg.locals.KEYDOWN, key=pg.locals.K_RETURN, mod=pg.locals.KMOD_NONE)
            pg.event.post(newevent)
        elif input_type == self.INPUT_DOWN:
            #Simulate a joystick 'down' input
            newevent = pg.event.Event(pg.JOYHATMOTION, value=(0, -1))
            pg.event.post(newevent)
        else:
            return

    def btn_select(self, client, userdata, message):
        """ Displays a text if the 'select' button is pressed
        """
        try:
            if(str(message.payload.decode("utf-8")) == "true"):
                if self.debug==True: print("Select key pressed\r")
                self.simulate_input(self.INPUT_SELECT)
        except Exception:
            print("ERROR in btn_select\n")

    def btn_down(self, client, userdata, message):
        """ Displays a text if the 'down' button is pressed
        """
        try:
            if(str(message.payload.decode("utf-8")) == "true"):
                if self.debug==True: print("Down key pressed\r")
                self.simulate_input(self.INPUT_DOWN)
        except Exception:
            print("ERROR in btn_down\n")
