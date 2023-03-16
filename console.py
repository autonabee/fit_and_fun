import pygame as pg
import pygame_menu as pg_menu
from pygame_menu import themes, Theme, widgets
from functools import partial
import database as db
import pygame_vkeyboard as vkboard
import sqlite3
import random as rand


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

COLOR_STAGE = pg.Color(115, 180, 20)
VALUES_TEMPS = [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90]
VALUES_RESISTANCE = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]


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
    green_button = pg_menu.baseimage.BaseImage(dir_img+'/button_green.png')
    yellow_button = pg_menu.baseimage.BaseImage(dir_img+'/button_yellow.png')
    red_button = pg_menu.baseimage.BaseImage(dir_img+'/button_red.png')
    gray_button = pg_menu.baseimage.BaseImage(dir_img+'/button_gray.png')
    stone_background = pg_menu.baseimage.BaseImage(dir_img+'/stone_background.png')

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
        self.current_user='Julien'
        # Wind resistor
        self.wind_resistor = wind

        self.current_exercise = 'Echauffement'

        self.guest_mode = False


    def set_wind(self):
        """ Activate the wind if the object exists"""
        if self.wind_resistor != None:
            self.wind_resistor.activate()
   

    def set_user(self, username, name): 
        """ callback called by self.usermenu """
        self.current_user=name


    def go_to_select_game_ui(self, is_guest_mode):
        self.guest_mode = is_guest_mode
        self.display_select_game_ui()


    def display_select_user_ui(self):
        list_users = db.get_all_user_tuples()
        self.current_user = list_users[0][0]

        select_user_ui = pg_menu.Menu('SELECTIONNEZ UN JOUEUR', self.size_x, self.size_y, theme=mytheme)
        user_label = select_user_ui.add.label('NOM D\'UTILISATEUR')
        selection_effect = pg_menu.widgets.HighlightSelection(0, 0, 0)
        user_dropselect = select_user_ui.add.dropselect('', list_users, default = 0, onchange=self.set_user, open_middle=True, placeholder_add_to_selection_box=False, margin=(0,0), selection_box_height=8)
        user_dropselect.set_selection_effect(selection_effect)
        frame = select_user_ui.add.frame_v(max(user_label.get_width(), user_dropselect.get_width()) + 30, user_label.get_height() + user_dropselect.get_height() + 30, background_color=self.stone_background)
        select_user_ui.add.vertical_margin(10)
        select_user_ui.add.button('VALIDER', partial(self.go_to_select_game_ui, False), background_color=self.green_button)
        select_user_ui.add.vertical_margin(30)
        select_user_ui.add.button('NOUVEAU JOUEUR', self.display_create_user_ui, background_color=self.yellow_button)
        select_user_ui.add.button('MODE INVITE', partial(self.go_to_select_game_ui, True), background_color=self.yellow_button)
        select_user_ui.add.vertical_margin(30)
        select_user_ui.add.button('HISTORIQUE', self.display_history_ui, background_color=self.yellow_button)
        select_user_ui.add.vertical_margin(30)
        select_user_ui.add.button('QUITTER', pg_menu.events.EXIT, background_color=self.red_button)

        frame.pack(user_label, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame.pack(user_dropselect, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
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
            user_dropselect.draw_after_if_selected(self.screen)
            pg.display.update()


    def set_game(self, game_name, game):
        self.game = game


    def display_select_game_ui(self):

        list_games = db.get_all_game_tuples()

        select_game_ui = pg_menu.Menu('SELECTIONNEZ UN JEU', self.size_x, self.size_y, theme=mytheme)
        select_game_ui.add.selector('', list_games, default=0, onchange=self.set_game)
        if not self.guest_mode:
            select_game_ui.add.button('VALIDER', self.display_select_exercise_ui)
        else:
            select_game_ui.add.button('VALIDER', self.set_parameters)
        if not self.guest_mode: select_game_ui.add.button('STATISTIQUES', self.display_stats_ui)
        select_game_ui.add.button('RETOUR', self.display_select_user_ui)
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
        self.current_exercise = exercise_value


    def display_select_exercise_ui(self):

        list_exercises = db.get_all_exercise_tuples()
        
        is_default_ex_selected = self.current_exercise == 'Echauffement'
        
        def delete_exercise():
            if not is_default_ex_selected:
                db.delete_all_stages_from_ex(self.current_exercise)
                db.delete_exercise(self.current_exercise)
                list_exercises = db.get_all_exercise_tuples()
                self.current_exercise = 'Echauffement'
                exercise_dropselect.update_items(list_exercises)
            else:
                #TODO Add a little feedback
                if self.debug: print("Can't delete default exercise")
                return
            

        select_exercise_ui = pg_menu.Menu('SELECTIONNEZ UN EXERCICE', self.size_x, self.size_y, theme=mytheme)
        exercise_dropselect = select_exercise_ui.add.dropselect('EXERCICE :', list_exercises, default = list_exercises.index((self.current_exercise, self.current_exercise)), onchange=self.set_exercise)
        select_exercise_ui.add.button('JOUER', self.set_parameters)
        select_exercise_ui.add.button('MODIFIER EXERCICE', partial(self.display_define_exercise_ui, False))
        select_exercise_ui.add.button('NOUVEL EXERCICE', partial(self.display_define_exercise_ui, True))
        button_delete = select_exercise_ui.add.button('SUPPRIMER', delete_exercise)
        select_exercise_ui.add.button('RETOUR', self.display_select_game_ui)
        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()
            
            is_default_ex_selected = self.current_exercise == 'Echauffement'
            
            if not is_default_ex_selected:
                button_delete.set_font(pg_menu.font.FONT_NEVIS, 28, (204,0,0,0), (200,200,200,50), (255,255,255), (255,255,255), (255,255,255,0))
            else:
                button_delete.set_font(pg_menu.font.FONT_NEVIS, 28, (200,200,200,50), (200,200,200,50), (255,255,255), (255,255,255), (255,255,255,0))

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    self.synchro.release()

            select_exercise_ui.update(events)

            select_exercise_ui.draw(self.screen)
            pg.display.update()


    def display_define_exercise_ui(self, is_new_exercise):
        """Displays the exercise definition ui
        
        Args:
            is_new_exercise (bool): if True, create a new exercise. If False, edit one existing
        """

        def delete_stage(id):
            """Delete the desired stage from the exercise definition ui

            Args:
                index (int): Index of the stage to be deleted (Warning: starting at 1, not 0)
            """
            index_label = label_widgets.index(define_exercise_ui.get_widget('label'+str(id)))
            for i in range(index_label + 1, len(label_widgets)) :
                define_exercise_ui.get_widget(label_widgets[i].get_id()).set_title('Etape ' + str(i))
            label_widgets.pop(index_label)
            stages_data.pop(index_label)
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('label' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('remove_button' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('temps' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('resistance' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('frame_global' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('frame_param' + str(id)))

        def add_stage(stage_values):
            """Add new stage into the exercise

            Args:
                stage_values (dict): dict containing "temps" and "resistance" values, None if new stage
            """
            if stage_values == None :
                stages_data.append(dict(temps=20, resistance=1))
            else :
                stages_data.append(stage_values)
            
            # On retire le bouton "Ajouter"
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('add_stage_button'))
            
            try:
                i = id_counter[0]
                id_counter[0] = id_counter[0] + 1
                color = COLOR_STAGE
                label = define_exercise_ui.add.label('Etape ' + str(len(label_widgets)+1), label_id='label'+str(i), align=pg_menu.locals.ALIGN_LEFT, font_color=(230, 230, 230))
                remove_button = define_exercise_ui.add.button('X', button_id='remove_button'+str(i), action=partial(delete_stage, i), align=pg_menu.locals.ALIGN_RIGHT, font_color=(230, 230, 230))
                temps = define_exercise_ui.add.range_slider('Temps : ', rangeslider_id='temps'+str(i), onchange=partial(change_time, i), font_color=(230, 230, 230), default=stages_data[-1]["temps"], range_text_value_enabled=False, range_values=VALUES_TEMPS)
                resistance = define_exercise_ui.add.range_slider('Resistance : ', rangeslider_id='resistance'+str(i), onchange=partial(change_resistance, i), font_color=(230, 230, 230), default=stages_data[-1]["resistance"], range_text_value_enabled=False, range_values=VALUES_RESISTANCE)
                frame_global = define_exercise_ui.add.frame_h(580, 140, frame_id='frame_global'+str(i), background_color=color, margin=(0,5))
                frame_global.relax(True)
                frame_global.pack(label, align=pg_menu.locals.ALIGN_LEFT)
                frame_global.pack(remove_button, align=pg_menu.locals.ALIGN_RIGHT)
                frame_param = define_exercise_ui.add.frame_v(400, 100, frame_id='frame_param'+str(i))
                frame_param.pack(temps, align=pg_menu.locals.ALIGN_CENTER)
                frame_param.pack(resistance, align=pg_menu.locals.ALIGN_CENTER)
                frame_global.pack(frame_param, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
                define_exercise_ui.select_widget(None)
                label_widgets.append(label)
            except KeyError:
                print("Wrong dictionary format when adding new stage")
                pg.display.quit()
                if self.debug: print("Quit") 
                self.synchro.release()
            
            # On replace le bouton "Ajouter"
            define_exercise_ui.add.button('+', button_id='add_stage_button', action=partial(add_stage, None), align=pg_menu.locals.ALIGN_CENTER, font_color=(0,150,0), border_width=2, border_color=(0,150,0), background_color=(0,255,0,100))

        def change_time(index, value):
            """Update time parameter in stages table

            Args:
                text (str): time value for this stage
                index (int): index of the stage you want to update
            """
            id = label_widgets.index(define_exercise_ui.get_widget('label'+str(index)))
            if self.debug and value != stages_data[id]["temps"]: print('Temps of stage ' + str(id+1) + " changed to " + str(value))
            stages_data[id]["temps"] = value

        def change_resistance(index, value):
            """Update resistance parameter in stages table

            Args:
                text (str): resistance value for this stage
                index (int): index of the stage you want to update
            """
            id = label_widgets.index(define_exercise_ui.get_widget('label'+str(index)))
            if self.debug and value != stages_data[id]["resistance"]: print('Resistance of stage ' + str(id+1) + " changed to " + str(value))
            stages_data[id]["resistance"] = value

        def quit_ui(is_saved):
            """Returns to previous ui

            Args:
                is_saved (bool): if True, save changes made to steps into the database
            """
            if is_saved:
                if is_save_active:
                    if is_new_exercise:
                        self.current_exercise = name_exercise.get_value()
                        db.create_new_exercise(name_exercise.get_value(), self.current_user)
                        for s_data in stages_data:
                            db.create_new_stage(self.current_exercise, s_data["temps"], s_data["resistance"])
                    else:
                        db.delete_all_stages_from_ex(self.current_exercise)
                        for s_data in stages_data:
                            db.create_new_stage(self.current_exercise, s_data["temps"], s_data["resistance"])
                    self.display_select_exercise_ui()
                else:
                    #TODO Add a little feedback
                    if self.debug: print("Exercise name already existing in the database")
                    return
            else:
                self.current_exercise = 'Echauffement'
                self.display_select_exercise_ui()
            

        stages_data = [] # Is filled in add stage, no need to fill it beforehand

        label_widgets = []

        if is_new_exercise: self.current_exercise = ''

        # Used to determined whether the prompted name is already existing or not
        existing_names = db.get_all_exercise_names()
        is_save_active = True

        id_counter = [1] # For all widgets to have an different id

        define_exercise_ui = pg_menu.Menu('DEFINISSEZ UN EXERCICE', self.size_x, self.size_y, theme=mytheme)
        
        if is_new_exercise:
            name_exercise = define_exercise_ui.add.text_input('Nom de l\'exercice :', margin=(0, 50), font_color=(0, 0, 0), background_color=(50,50,50,150))
        else:
            name_exercise = define_exercise_ui.add.label(self.current_exercise, margin=(0, 50), font_color=(0, 0, 0), background_color=(50,50,50,150))
        define_exercise_ui.add.button('+', button_id='add_stage_button', action=partial(add_stage, None), align=pg_menu.locals.ALIGN_CENTER, font_color=(0,150,0), border_width=2, border_color=(0,150,0), background_color=(0,255,0,100))
        button_cancel = define_exercise_ui.add.button('ANNULER', action=partial(quit_ui, False))
        button_cancel.set_font(pg_menu.font.FONT_NEVIS, 24, (0,0,0), (255,255,255), (255,255,255), (255,255,255), (255,255,255,0))
        button_save = define_exercise_ui.add.button('ENREGISTRER', action=partial(quit_ui, True))
        
        stored_stages = []
        if not is_new_exercise:
            stages_from_db = db.get_all_stages_from_ex(self.current_exercise)
            print(stages_from_db)
            for stage in stages_from_db:
                stored_stages.append(dict(temps = stage[2], resistance = stage[3]))
            for i in range(0, len(stored_stages)):
                add_stage(stored_stages[i])
        else :
            for i in range(0, 3):
                add_stage(None)

        layout = vkboard.VKeyboardLayout(vkboard.VKeyboardLayout.AZERTY)
        def on_key_event(text):
            name_exercise.set_value(text)
            if self.debug: print(name_exercise.get_value())
            return
        
        keyboard = vkboard.VKeyboard(define_exercise_ui,
                                    on_key_event,
                                    layout,
                                    renderer=vkboard.VKeyboardRenderer.DARK,
                                    show_text=False)

        while True:
            time_delta = self.clock.tick(60)/1000.0

            if is_new_exercise:
                is_kb_active = name_exercise.get_selected_time() != 0
            else:
                is_kb_active = False

            if is_new_exercise and (name_exercise.get_value() == '' or name_exercise.get_value() in existing_names):
                is_save_active = False
                button_save.set_font(pg_menu.font.FONT_NEVIS, 28, (200,200,200,50), (200,200,200,50), (255,255,255), (255,255,255), (255,255,255,0))
            else:
                is_save_active = True
                button_save.set_font(pg_menu.font.FONT_NEVIS, 28, (0,204,0), (255,255,255), (255,255,255), (255,255,255), (255,255,255,0))

            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit")
                    self.synchro.release()
                elif event.type == pg.FINGERDOWN:
                    events.remove(event) # Avoid double event (FINGERDOWN and MOUSEDOWN) when using touchscreen

            define_exercise_ui.update(events)
            if is_kb_active: keyboard.update(events)
            define_exercise_ui.draw(self.screen)
            if is_kb_active: rects = keyboard.draw(self.screen, True)

            # Flip only the updated area
            pg.display.update()
            if is_kb_active: pg.display.update(rects)


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
        print('Displays delete user ui')
        return

        
    def display_create_user_ui(self):

        def create_user(name_input):
            if is_save_active:
                name = name_input.get_value()
                db.create_new_user(name)
                self.display_select_game_ui()
            else:
                #TODO Add a little feedback
                if self.debug: print("Exercise name alreadung existing in the database")
                return

        create_user_ui = pg_menu.Menu('NEW USER', self.size_x, self.size_y, theme=mytheme)
        name_input = create_user_ui.add.text_input("Nom : ")
        button_save = create_user_ui.add.button('VALIDER', action=partial(create_user, name_input))
        create_user_ui.add.button('RETOUR', self.display_select_user_ui)
        
        layout = vkboard.VKeyboardLayout(vkboard.VKeyboardLayout.AZERTY)

        def on_key_event(text):
            name_input.set_value(text)
            if self.debug: print(name_input.get_value())

        keyboard = vkboard.VKeyboard(create_user_ui,
                                    on_key_event,
                                    layout,
                                    renderer=vkboard.VKeyboardRenderer.DARK,
                                    show_text=False)
        
        is_save_active = False
        existing_names = db.get_all_user_names()

        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()

            if name_input.get_value() == '' or name_input.get_value() in existing_names:
                is_save_active = False
                button_save.set_font(pg_menu.font.FONT_NEVIS, 28, (200,200,200,50), (200,200,200,50), (255,255,255), (255,255,255), (255,255,255,0))
            else:
                is_save_active = True
                button_save.set_font(pg_menu.font.FONT_NEVIS, 28, (0,204,0), (255,255,255), (255,255,255), (255,255,255), (255,255,255,0))

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug: print("Quit") 
                    self.synchro.release()
                elif event.type == pg.FINGERDOWN:
                    #Avoid double event (FINGERDOWN and MOUSEDOWN) when using touchscreen
                    events.remove(event)

            create_user_ui.update(events)
            keyboard.update(events)
            create_user_ui.draw(self.screen)
            rects = keyboard.draw(self.screen, True)

            # Flip only the updated area
            pg.display.update()
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
