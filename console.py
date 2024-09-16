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

import pygame as pg
import pygame_menu as pg_menu
from pygame_menu import themes, Theme, widgets
from functools import partial
import database as db
import pygame_vkeyboard as vkboard
import statistics
from game_canoe import GameCanoe
from game_data import GameData


import threading
import time
import os
import sys

class Console():
    """ Class Console to manage the game
        using a single input rot_speed
        It provides a method get_speed to be called outside
        of the class to read a 'sensor value'
    """
    
    #Images
    dir_img=os.path.join(os.path.dirname(__file__), 'images')
    
    hourglass = pg.image.load(dir_img+'/hourglass.png')
    connection_ok = pg.image.load(dir_img+'/connection_ok.png')
    connection_failure = pg.image.load(dir_img+'/connection_failure.png')
    green_button        = pg_menu.baseimage.BaseImage(dir_img+'/button_green.png')
    yellow_button       = pg_menu.baseimage.BaseImage(dir_img+'/button_yellow.png')
    red_button          = pg_menu.baseimage.BaseImage(dir_img+'/button_red.png')
    gray_button         = pg_menu.baseimage.BaseImage(dir_img+'/button_gray.png')
    stone_background    = pg_menu.baseimage.BaseImage(dir_img+'/stone_background.png')
    wood_background     = pg_menu.baseimage.BaseImage(dir_img+'/wood_background.png')
    jewel_background    = pg_menu.baseimage.BaseImage(dir_img+'/jewel_background.png')

    icon_chrono         = pg_menu.baseimage.BaseImage(dir_img+'/icon_chrono.png')
    icon_arrive         = pg_menu.baseimage.BaseImage(dir_img+'/icon_arrive.png')
    icon_snail          = pg_menu.baseimage.BaseImage(dir_img+'/icon_snail.png')
    icon_hourglass      = pg_menu.baseimage.BaseImage(dir_img+'/icon_hourglass.png')

    icon_pedal          = pg_menu.baseimage.BaseImage(dir_img+'/icon_pedal.png')
    icon_keyboard       = pg_menu.baseimage.BaseImage(dir_img+'/icon_keyboard.png')

    clock = pg.time.Clock()
    
    def __init__(self, wind=None, debug=False, fullscreen=False, orientation='portrait'):
        """ Class constructor """
#Declaration des varibales
        # Custom menu theme
        self.mytheme = pg_menu.themes.THEME_DEFAULT.copy()
        if orientation == 'portrait':
            myimage = pg_menu.baseimage.BaseImage(image_path=os.path.join(os.path.dirname(__file__),"images/menu_bg_portrait.png"))
        else:
            myimage = pg_menu.baseimage.BaseImage(image_path=os.path.join(os.path.dirname(__file__),"images/menu_bg_landscape.png"))
        self.mytheme.background_color = myimage
        self.mytheme.widget_font=pg_menu.font.FONT_NEVIS

        # Min/Max speed 
        self.ROT_SPEED_MIN = 00
        self.ROT_SPEED_MAX = 15
        # rot speed max = 700, screen speed max = 3 => 3/600

        # Selectable values in exercise definition
        self.VALUES_TEMPS_M = []
        for i in range(0,61,1):
            self.VALUES_TEMPS_M.append((str(i)+'m', i)) # Between 0 and 30 minutes
            
        self.VALUES_TEMPS_S = []
        for i in range(0,56,5):
            self.VALUES_TEMPS_S.append((str(i)+'s', i)) # Between 0 and 55 seconds

        self.VALUES_RESISTANCE = [] #Also used for difficulty
        for i in range(1,16):
            self.VALUES_RESISTANCE.append((str(i)+'/15', i)) # Between 1 and 15 (arbitrary values)
        
        self.VALUES_VITESSE = [] 
        for i in range(1,16):
            self.VALUES_VITESSE.append((str(i)+'/15', i)) # Between 1 and 15 (arbitrary values)

        # Number of frames before the sensor is considered disconnected
        self.TIMEOUT_TOLERANCE = 30

        # Control variable
        self._on_message = None
        # raw speed value received from the mqtt sensor
        self.rot_speed=0  #radian/sec
        # initial time when the boat pass the GO line
        self.timebegin=0
        
        # Screen init
        pg.init()
        self.orientation = orientation
        if fullscreen:
            self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
            self.size_x = self.screen.get_width()
            self.size_y = self.screen.get_height()
        else:
            if orientation == 'portrait':
                self.size_x = 600
                self.size_y = 988
            else:
                self.size_x = 988
                self.size_y = 600
            self.screen = pg.display.set_mode((self.size_x, self.size_y))
        pg.display.set_caption('Fit&Fun')
        #Add a delay before you can press a key again
        pg.key.set_repeat(150)
        # Font, Colors
        self.font_name = pg.font.match_font('arial')
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHTGRAY = (220, 220, 220)
        self.DARKGRAY = (140, 140, 140)
        self.RED = (255, 0, 56)
        
        # lock for synchro to kill the sensor speed client
        self.synchro = threading.Lock()
        self.debug=debug
        self.difficulty=1
        # Wind resistor
        self.wind_resistor = wind

        self.current_user='everybody'
        self.current_game=('What The Duck','GameCanoe')
        self.current_exercise = 'Echauffement'
        self.stages = [(0,1,120,1,1)] # Initialization in game_canoe
        self.current_stage = self.stages[0]
        self.current_diff = None # Used only in demo mode

        self.demo_mode = False

        self.kb_input = False

        self.speed_values = []
        self.speed_means = []

        self.connection_timeout = self.TIMEOUT_TOLERANCE


    def set_wind(self):
        """ Activate the wind if the object exists"""
        if self.wind_resistor != None:
            self.wind_resistor.activate()
   

    def set_user(self, username, name): 
        """ Update current user name with data coming from a dropselect """
        self.current_user=name


    def launch_selected_game(self, is_demo_mode, is_kb_input):
        """ Launch the selected game applying a certain configuration depending on the context """

        self.kb_input = is_kb_input
        if is_demo_mode: 
            stages = [self.current_diff]
        else:            
            stages = db.get_all_stages_from_ex(self.current_exercise)
            # Transform ex_id datebase in index 
            for index, stage in enumerate(stages):
                stages[index]=(stage[0], index+1, stage[2], stage[3], stage[4], stage[5])

        if self.current_game[1] == 'GameCanoe':
            game = GameCanoe(self, stages)
        elif self.current_game[1] == 'GameData':
            game = GameData(self, stages)
        game.game()


    def display_select_difficulty_ui(self):
        """ Displays the difficulty selection ui """

        self.current_diff = (0,1,120,1,1)

        def set_diff(selected_tuple, value):
            self.current_diff = value
            if self.debug: print('Difficulty set to ' + selected_tuple[0][0])

        def launch_game():
            self.launch_selected_game(True, input_toggle.get_value())

        select_diff_ui = pg_menu.Menu('MODE DEMO', self.size_x, self.size_y, theme=self.mytheme)
        
        selection_effect = pg_menu.widgets.HighlightSelection(0, 0, 0)
        diff_label = select_diff_ui.add.label('DIFFICULTE')
        diff_dropselect = select_diff_ui.add.dropselect('', [('Facile',(0,1,120,1,1)),('Moyen',(0,1,120,1,5)),('Difficile',(0,1,120,1,10)),('Chaotique',(0,1,120,1,15))],
                                                    default = 0, onchange=set_diff, open_middle=True, placeholder_add_to_selection_box=False, padding=(5,30,5,0), selection_box_height=4)
        diff_dropselect.set_selection_effect(selection_effect)
        input_toggle = select_diff_ui.add.toggle_switch(' ', state_text=('Maindalier','Clavier'), state_color=((178,178,178),(178,178,178)), width=200, padding=(5,30,5,0))
        input_toggle.set_selection_effect(selection_effect)
        pedal_image = select_diff_ui.add.image(self.icon_pedal)
        keyboard_image = select_diff_ui.add.image(self.icon_keyboard)
        frame_toggle = select_diff_ui.add.frame_h(pedal_image.get_width() + keyboard_image.get_width() + input_toggle.get_width() + 50, 70)
        frame_toggle.pack(pedal_image, align=pg_menu.locals.ALIGN_CENTER)
        frame_toggle.pack(input_toggle, align=pg_menu.locals.ALIGN_CENTER)
        frame_toggle.pack(keyboard_image, align=pg_menu.locals.ALIGN_CENTER)
        frame = select_diff_ui.add.frame_v(frame_toggle.get_width() + 30, diff_label.get_height() + diff_dropselect.get_height() + frame_toggle.get_height() + 30, background_color=self.stone_background)
        frame.pack(diff_label, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame.pack(diff_dropselect, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame.pack(frame_toggle, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        select_diff_ui.add.vertical_margin(30)

        select_diff_ui.add.button('JOUER', launch_game, background_color=self.green_button)
        select_diff_ui.add.vertical_margin(30)
        select_diff_ui.add.button('RETOUR', self.display_select_user_ui, background_color=self.yellow_button)
        
        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    if self.synchro.locked():
                        self.synchro.release()
                    sys.exit()

            select_diff_ui.update(events)

            select_diff_ui.draw(self.screen)
            diff_dropselect.draw_after_if_selected(self.screen)

            # Displays connection icon
            if self.connection_timeout > 0: self.screen.blit(self.connection_ok, (5,self.size_y-35))
            else:                           self.screen.blit(self.connection_failure, (5,self.size_y-35))
            self.connection_timeout = self.connection_timeout - 1

            pg.display.update()


    def display_select_user_ui(self):
        """ Displays the user selection ui """

        def delete_user():
            """ Displays the user deletion ui (doesn't if the default user is selected)"""
            if is_save_active:
                self.display_delete_user_ui()
            else:
                if self.debug: print("Can't delete default user")
                return
        
        def go_to_select_game_ui():
            """ Displays the game selection ui """
            self.demo_mode = False
            self.display_select_game_ui()

        def go_to_select_difficulty_ui():
            """ Displays a light version of the interface which doesn't have any link with the database """
            self.demo_mode = True
            self.display_select_difficulty_ui()
        
        # Fetch existing users in the database
        list_users = db.get_all_user_tuples()
        self.current_user = list_users[0][0]

        select_user_ui = pg_menu.Menu('CHOIX DU PROFIL', self.size_x, self.size_y, theme=self.mytheme)
        
        user_label = select_user_ui.add.label('NOM D\'UTILISATEUR')
        selection_effect = pg_menu.widgets.HighlightSelection(0, 0, 0)
        user_dropselect = select_user_ui.add.dropselect('', list_users, default = 0, onchange=self.set_user, placeholder_add_to_selection_box=False, margin=(0,0), selection_box_height=8)
        user_dropselect.set_selection_effect(selection_effect)
        
        frame = select_user_ui.add.frame_v(max(user_label.get_width(), user_dropselect.get_width()) + 30, user_label.get_height() + user_dropselect.get_height() + 30, background_color=self.stone_background)
        frame.pack(user_label, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame.pack(user_dropselect, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        select_user_ui.add.vertical_margin(10)
        select_user_ui.add.button('VALIDER', go_to_select_game_ui, background_color=self.green_button)
        select_user_ui.add.vertical_margin(30)
        select_user_ui.add.button('NOUVEAU JOUEUR', self.display_create_user_ui, background_color=self.yellow_button)
        select_user_ui.add.vertical_margin(5)
        select_user_ui.add.button('MODE DEMO', go_to_select_difficulty_ui, background_color=self.yellow_button)
        select_user_ui.add.vertical_margin(30)
        delete_button = select_user_ui.add.button('SUPPRIMER LE JOUEUR', delete_user, background_color=self.red_button)
        select_user_ui.add.vertical_margin(30)
        select_user_ui.add.button('QUITTER', pg_menu.events.EXIT, background_color=self.red_button)
        
        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    if self.synchro.locked():
                        self.synchro.release()
                    sys.exit()

            # Doesn't allow the suppression of the default user
            if self.current_user == 'everybody':
                is_save_active = False
                delete_button.set_font(pg_menu.font.FONT_NEVIS, 28, self.LIGHTGRAY, self.LIGHTGRAY, self.LIGHTGRAY, self.LIGHTGRAY, self.DARKGRAY)
                delete_button.set_background_color(self.gray_button)
            else:
                is_save_active = True
                delete_button.set_font(pg_menu.font.FONT_NEVIS, 28, (60,60,60), self.WHITE, self.WHITE, self.WHITE, self.RED)
                delete_button.set_background_color(self.red_button)

            select_user_ui.update(events)

            select_user_ui.draw(self.screen)
            user_dropselect.draw_after_if_selected(self.screen)

            # Displays connection icon
            if self.connection_timeout > 0: self.screen.blit(self.connection_ok, (5,self.size_y-35))
            else:                           self.screen.blit(self.connection_failure, (5,self.size_y-35))
            self.connection_timeout = self.connection_timeout - 1

            pg.display.update()


    def display_select_game_ui(self):
        """ Displays the game selection ui """

        def set_game(game_tuple, class_name):
            """ Update current game name with data coming from a dropselect """
            self.current_game = game_tuple[0]

        # Fetch existing games in the database
        list_games = db.get_all_game_tuples()

        select_game_ui = pg_menu.Menu('CHOIX DU JEU', self.size_x, self.size_y, theme=self.mytheme)

        game_label = select_game_ui.add.label('JEU')
        selection_effect = pg_menu.widgets.HighlightSelection(0, 0, 0)
        game_dropselect = select_game_ui.add.dropselect('', list_games, default = list_games.index(self.current_game), onchange=set_game, open_middle=True, placeholder_add_to_selection_box=False, margin=(0,0), selection_box_height=8)
        game_dropselect.set_selection_effect(selection_effect)
        frame = select_game_ui.add.frame_v(max(game_label.get_width(), game_dropselect.get_width()) + 30, game_label.get_height() + game_dropselect.get_height() + 30, background_color=self.stone_background)
        frame.pack(game_label, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame.pack(game_dropselect, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        select_game_ui.add.vertical_margin(10)
        select_game_ui.add.button('VALIDER', self.display_select_exercise_ui, background_color=self.green_button)
        select_game_ui.add.vertical_margin(30)
        select_game_ui.add.button('STATISTIQUES', self.display_stats_ui, background_color=self.yellow_button)
        select_game_ui.add.vertical_margin(30)
        select_game_ui.add.button('RETOUR', self.display_select_user_ui, background_color=self.yellow_button)
        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit")
                    if self.synchro.locked():
                        self.synchro.release()
                    sys.exit()

            select_game_ui.update(events)

            select_game_ui.draw(self.screen)
            game_dropselect.draw_after_if_selected(self.screen)

            # Displays connection icon
            if self.connection_timeout > 0: self.screen.blit(self.connection_ok, (5,self.size_y-35))
            else:                           self.screen.blit(self.connection_failure, (5,self.size_y-35))
            self.connection_timeout = self.connection_timeout - 1

            user_name = pg.font.Font('freesansbold.ttf', 24).render(self.current_user, True, (255,255,255), None)
            user_name_rect = user_name.get_rect()
            user_name_rect.center = (self.screen.get_width()-user_name_rect.width/2-5,self.screen.get_height()-user_name_rect.height/2-5)
            self.screen.blit(user_name, user_name_rect)

            pg.display.update()


    def set_exercise(self, exercise_display, exercise_value):
        """ Update current exercise name with data coming from a dropselect"""
        self.current_exercise = exercise_value


    def display_select_exercise_ui(self):
        """ Displays the exercise selection ui """

        # Fetch existing exercises in the database
        list_exercises = db.get_all_exercise_tuples()     
        is_default_ex_selected = self.current_exercise == 'Echauffement'
        # Note : For now, the 'Echauffement' exercise is here as a default value
        # Thus, it is impossible to either delete it or to edit it via the user interface
        
        def delete_exercise():
            """ Delete the selected exercise from the db and reload the dropselect """
            
            if not is_default_ex_selected:
                db.delete_all_stages_from_ex(self.current_exercise)
                db.delete_exercise(self.current_exercise)
                list_exercises = db.get_all_exercise_tuples()
                self.current_exercise = 'Echauffement'
                ex_dropselect.update_items(list_exercises)
            else:
                if self.debug: print("Can't delete default exercise")
                return
            
        def define_exercise(is_new):
            """ Displays the exercise edition interface """
            
            if is_new:
                self.screen.blit(self.hourglass, (self.size_x/2-50,self.size_y/2-60))
                pg.display.update()
                select_exercise_ui.draw(self.screen)
                self.display_define_exercise_ui(True)
            else:
                # Check if the selected exercise is 'Echauffement'
                if not is_default_ex_selected:
                    self.screen.blit(self.hourglass, (self.size_x/2-50,self.size_y/2-60))
                    pg.display.update()
                    select_exercise_ui.draw(self.screen)
                    self.display_define_exercise_ui(False)
                else:
                    if self.debug: print("Can't edit default exercise")
                    return
            
        def launch_game():
            """ Launch the game applying configuration from the selected exercise """
            self.launch_selected_game(False, input_toggle.get_value())

        select_exercise_ui = pg_menu.Menu('CHOIX DE L\'EXERCICE', self.size_x, self.size_y, theme=self.mytheme)

        ex_label = select_exercise_ui.add.label('EXERCICE')
        selection_effect = pg_menu.widgets.HighlightSelection(0, 0, 0)
        ex_dropselect = select_exercise_ui.add.dropselect('', list_exercises, default = list_exercises.index((self.current_exercise, self.current_exercise)),
                                                                    onchange=self.set_exercise, placeholder_add_to_selection_box=False, margin=(0,0), selection_box_height=8, padding=(5,30,5,0))
        ex_dropselect.set_selection_effect(selection_effect)
        input_toggle = select_exercise_ui.add.toggle_switch(' ', state_text=('Maindalier','Clavier'), state_color=((178,178,178),(178,178,178)), width=200, padding=(5,30,5,0))
        input_toggle.set_selection_effect(selection_effect)
        pedal_image = select_exercise_ui.add.image(self.icon_pedal)
        keyboard_image = select_exercise_ui.add.image(self.icon_keyboard)
        frame_toggle = select_exercise_ui.add.frame_h(pedal_image.get_width() + keyboard_image.get_width() + input_toggle.get_width() + 50, 70)
        frame_toggle.pack(pedal_image, align=pg_menu.locals.ALIGN_CENTER)
        frame_toggle.pack(input_toggle, align=pg_menu.locals.ALIGN_CENTER)
        frame_toggle.pack(keyboard_image, align=pg_menu.locals.ALIGN_CENTER)
        frame = select_exercise_ui.add.frame_v(frame_toggle.get_width() + 30, ex_label.get_height() + ex_dropselect.get_height() + frame_toggle.get_height() + 30, background_color=self.stone_background)
        frame.pack(ex_label, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame.pack(ex_dropselect, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame.pack(frame_toggle, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        select_exercise_ui.add.vertical_margin(10)
        select_exercise_ui.add.button('JOUER', launch_game, background_color=self.green_button)
        select_exercise_ui.add.vertical_margin(30)
        button_edit = select_exercise_ui.add.button('MODIFIER EXERCICE', partial(define_exercise, False), background_color=self.yellow_button)
        select_exercise_ui.add.vertical_margin(5)
        select_exercise_ui.add.button('NOUVEL EXERCICE', partial(define_exercise, True), background_color=self.green_button)
        select_exercise_ui.add.vertical_margin(30)
        button_delete = select_exercise_ui.add.button('SUPPRIMER', delete_exercise)
        select_exercise_ui.add.vertical_margin(30)
        select_exercise_ui.add.button('RETOUR', self.display_select_game_ui, background_color=self.yellow_button)
        
        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()
            
            # Doesn't allow deletion or edition if select exercise is 'Echauffement'
            is_default_ex_selected = self.current_exercise == 'Echauffement'
            if not is_default_ex_selected:
                button_delete.set_font(pg_menu.font.FONT_NEVIS, 28, (80,80,80), self.WHITE, self.WHITE, self.WHITE, (255,255,255,0))
                button_delete.set_background_color(self.red_button)
                button_edit.set_font(pg_menu.font.FONT_NEVIS, 28, (80,80,80), self.WHITE, self.WHITE, self.WHITE, (255,255,255,0))
                button_edit.set_background_color(self.yellow_button)
            else:
                button_delete.set_font(pg_menu.font.FONT_NEVIS, 28, (200,200,200,50), self.WHITE, self.WHITE, self.WHITE, (255,255,255,0))
                button_delete.set_background_color(self.gray_button)
                button_edit.set_font(pg_menu.font.FONT_NEVIS, 28, (200,200,200), self.WHITE, self.WHITE, self.WHITE, (255,255,255,0))
                button_edit.set_background_color(self.gray_button)

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit")
                    if self.synchro.locked():
                        self.synchro.release()
                    sys.exit()

            select_exercise_ui.update(events)

            select_exercise_ui.draw(self.screen)
            ex_dropselect.draw_after_if_selected(self.screen)

            # Displays connection icon
            if self.connection_timeout > 0: self.screen.blit(self.connection_ok, (5,self.size_y-35))
            else:                           self.screen.blit(self.connection_failure, (5,self.size_y-35))
            self.connection_timeout = self.connection_timeout - 1

            user_name = pg.font.Font('freesansbold.ttf', 24).render(self.current_user, True, (255,255,255), None)
            user_name_rect = user_name.get_rect()
            user_name_rect.center = (self.screen.get_width()-user_name_rect.width/2-5,self.screen.get_height()-user_name_rect.height/2-5)
            self.screen.blit(user_name, user_name_rect)

            pg.display.update()


    def display_define_exercise_ui(self, is_new_exercise):
        """Displays the exercise definition ui
        
        Args:
            is_new_exercise (bool): if True, create a new exercise. If False, edit the one specified by self.cuurent_exercise
        """

        def delete_stage(id):
            """Delete the desired stage from the exercise definition ui

            Args:
                index (int): Index of the stage to be deleted
            """

            # Delete all traces of deleted stage in ids or stages_data and rename all following stages
            index_label = ids.index(id)
            for i in range(index_label + 1, len(ids)) :
                define_exercise_ui.get_widget('label'+str(ids[i])).set_title('Etape ' + str(i))
            ids.pop(index_label)
            stages_data.pop(index_label)

            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('label' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('remove_button' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('label_temps' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('temps_m' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('temps_s' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('frame_temps' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('resistance' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('difficulte' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('vitesse' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('frame_global' + str(id)))
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('frame_param' + str(id)))

        def add_stage(stage_values, loading_image):
            """Add new stage into the exercise

            Args:
                stage_values (dict): dict containing "temps", "resistance", "difficulte" and "vitesse" values, None if new stage
            """

            if loading_image :
                self.screen.blit(self.hourglass, (self.size_x/2-50,self.size_y/2-60))
                pg.display.update()
                define_exercise_ui.draw(self.screen)

            if stage_values == None :
                stages_data.append(dict(temps=20, resistance=1, difficulte=1,vitesse=1))  # VALEUR VITESSE A MODIFIER EN FCT DE LA VALEUR ACCEPTEE
            else :
                stages_data.append(stage_values)
            
            # Remove 'add' button to replace it at the end
            define_exercise_ui.remove_widget(define_exercise_ui.get_widget('add_stage_button'))
            
            try:
                # Keeping the list of used ids up to date
                if(len(ids) > 0):   
                    ids.append(ids[-1]+1)
                else:               
                    ids.append(1)
                i = ids[-1]
                label = define_exercise_ui.add.label('Etape ' + str(len(ids)), label_id='label'+str(i), align=pg_menu.locals.ALIGN_LEFT, font_color=(82, 41, 11), font_size=20)
                remove_button = define_exercise_ui.add.button('X', button_id='remove_button'+str(i), action=partial(delete_stage, i), align=pg_menu.locals.ALIGN_RIGHT, font_color=(82, 41, 11))
                temps_label = define_exercise_ui.add.label('Temps :', label_id='label_temps'+str(i), font_color=(230, 230, 230), font_size=24)
                temps_m = define_exercise_ui.add.selector('', self.VALUES_TEMPS_M, default=self.VALUES_TEMPS_M.index((str(stages_data[-1]["temps"]//60)+'m', stages_data[-1]["temps"]//60)), selector_id='temps_m'+str(i),
                                                       onchange=partial(change_time_m, i), font_color=(230, 230, 230), font_size=24)
                temps_s = define_exercise_ui.add.selector('', self.VALUES_TEMPS_S, default=self.VALUES_TEMPS_S.index((str(stages_data[-1]["temps"]%60)+'s', stages_data[-1]["temps"]%60)), selector_id='temps_s'+str(i),
                                                       onchange=partial(change_time_s, i), font_color=(230, 230, 230), font_size=24)
                resistance = define_exercise_ui.add.selector('Resistance : ', self.VALUES_RESISTANCE, default=self.VALUES_RESISTANCE.index((str(stages_data[-1]["resistance"])+'/15', stages_data[-1]["resistance"])), selector_id='resistance'+str(i),
                                                        onchange=partial(change_resistance, i), font_color=(230, 230, 230), font_size=24)
                difficulte = define_exercise_ui.add.selector('Difficulte : ', self.VALUES_RESISTANCE, default=self.VALUES_RESISTANCE.index((str(stages_data[-1]["difficulte"])+'/15', stages_data[-1]["difficulte"])), selector_id='difficulte'+str(i),
                                                        onchange=partial(change_difficulte, i), font_color=(230, 230, 230), font_size=24)
                vitesse = define_exercise_ui.add.selector('Vitesse : ', self.VALUES_VITESSE, default=self.VALUES_VITESSE.index((str(stages_data[-1]["vitesse"])+'/15', stages_data[-1]["vitesse"])), selector_id='vitesse'+str(i),
                                                        onchange=partial(change_vitesse, i), font_color=(230, 230, 230), font_size=24)
                frame_global = define_exercise_ui.add.frame_h(580, 150, frame_id='frame_global'+str(i), background_color=self.wood_background, margin=(0,5))
                frame_global.relax(True)
                frame_global.pack(label, align=pg_menu.locals.ALIGN_LEFT, vertical_position=pg_menu.locals.POSITION_NORTH)
                frame_global.pack(remove_button, align=pg_menu.locals.ALIGN_RIGHT, vertical_position=pg_menu.locals.POSITION_NORTH)
                frame_param = define_exercise_ui.add.frame_v(500, 200, frame_id='frame_param'+str(i))
                frame_temps = define_exercise_ui.add.frame_h(450, 44, frame_id='frame_temps'+str(i))
                frame_temps.pack(temps_label, align=pg_menu.locals.ALIGN_CENTER)
                frame_temps.pack(temps_m, align=pg_menu.locals.ALIGN_CENTER)
                frame_temps.pack(temps_s, align=pg_menu.locals.ALIGN_CENTER)
                frame_param.pack(frame_temps, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
                frame_param.pack(resistance, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
                frame_param.pack(difficulte, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
                frame_param.pack(vitesse, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
                frame_global.pack(frame_param, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
                define_exercise_ui.select_widget(None)
            except KeyError:
                print("Wrong dictionary format when adding new stage")
                pg.display.quit()
                if self.debug: print("Quit") 
                if self.synchro.locked():
                    self.synchro.release()
                sys.exit()
            
            # Replace 'add' button
            define_exercise_ui.add.button('+', button_id='add_stage_button', action=partial(add_stage, None, True), align=pg_menu.locals.ALIGN_CENTER, font_color=(0,150,0), border_width=2, border_color=(0,150,0), background_color=self.green_button)

        def change_time_m(index, item, value):
            """Update time parameter in stages table

            Args:
                index (int): index of the stage you want to update
            """
            id = ids.index(index)
            val_sec = stages_data[id]["temps"] % 60
            if self.debug and value != stages_data[id]["temps"] - val_sec: print('Duration of stage ' + str(id+1) + " changed to " + str(value*60 + val_sec) + " seconds")
            stages_data[id]["temps"] = value * 60 + val_sec

        def change_time_s(index, item, value):
            """Update time parameter in stages table

            Args:
                index (int): index of the stage you want to update
            """
            id = ids.index(index)
            val_min = stages_data[id]["temps"] // 60
            if self.debug and value != stages_data[id]["temps"] - val_min*60: print('Duration of stage ' + str(id+1) + " changed to " + str(val_min*60 + value) + " seconds")
            stages_data[id]["temps"] = val_min * 60 + value

        def change_resistance(index, item, value):
            """Update resistance parameter in stages table

            Args:
                text (str): resistance value for this stage
                index (int): index of the stage you want to update
            """
            id = ids.index(index)
            if self.debug and value != stages_data[id]["resistance"]: print('Resistance of stage ' + str(id+1) + " changed to " + str(value))
            stages_data[id]["resistance"] = value

        def change_difficulte(index, item, value):
            """Update difficulte parameter in stages table

            Args:
                text (str): difficulte value for this stage
                index (int): index of the stage you want to update
            """
            id = ids.index(index)
            if self.debug and value != stages_data[id]["difficulte"]: print('Difficulty of stage ' + str(id+1) + " changed to " + str(value))
            stages_data[id]["difficulte"] = value
            
        def change_vitesse(index, item, value):
            """Update difficulte parameter in stages table

            Args:
                text (str): difficulte value for this stage
                index (int): index of the stage you want to update
            """
            id = ids.index(index)
            if self.debug and value != stages_data[id]["vitesse"]: print('Vitesse of stage ' + str(id+1) + " changed to " + str(value))
            stages_data[id]["vitesse"] = value

        def quit_ui(is_saved):
            """Returns to previous ui

            Args:
                is_saved (bool): if True, save changes made to steps into the database
            """
            if is_saved:
                if is_save_active:
                    if is_new_exercise:
                        self.current_exercise = name_exercise_input.get_value()
                        db.create_new_exercise(name_exercise_input.get_value(), self.current_user)
                        for s_data in stages_data:
                            db.create_new_stage(self.current_exercise, s_data["temps"], s_data["resistance"], s_data["difficulte"], s_data["vitesse"])
                    else:
                        db.delete_all_stages_from_ex(self.current_exercise)
                        for s_data in stages_data:
                            db.create_new_stage(self.current_exercise, s_data["temps"], s_data["resistance"], s_data["difficulte"], s_data["vitesse"])
                    self.display_select_exercise_ui()
                else:
                    if self.debug: print("Exercise name already existing in the database")
                    return
            else:
                self.display_select_exercise_ui()
            
        stages_data = [] # Is filled in add stage, no need to fill it beforehand

        # Used to determined whether the prompted name is already existing or not
        existing_names = db.get_all_exercise_names()
        is_save_active = True

        # Used to keep in memory all used ids
        ids = []

        define_exercise_ui = pg_menu.Menu('CREATION', self.size_x, self.size_y, theme=self.mytheme)
        
        if is_new_exercise:
            name_exercise_label = define_exercise_ui.add.label('Nom de l\'exercice', font_color=self.WHITE)
            name_exercise_input = define_exercise_ui.add.text_input('', font_color=self.WHITE, border_color=self.WHITE, border_width=1)
            name_exercise_check = define_exercise_ui.add.button('OK', background_color=self.green_button, font_size=20)
            frame = define_exercise_ui.add.frame_v(400, name_exercise_label.get_height() + name_exercise_input.get_height() + name_exercise_check.get_height() + 30, background_color=self.stone_background)
            frame.pack(name_exercise_label, align=pg_menu.locals.ALIGN_CENTER)
            frame.pack(name_exercise_input, align=pg_menu.locals.ALIGN_CENTER)
            frame.pack(define_exercise_ui.add.vertical_margin(10))
            frame.pack(name_exercise_check, align=pg_menu.locals.ALIGN_CENTER)
        else:
            name_exercise_input = define_exercise_ui.add.label(self.current_exercise, font_color=self.WHITE, background_color=self.stone_background)
        define_exercise_ui.add.button('+', button_id='add_stage_button', action=partial(add_stage, None, True), align=pg_menu.locals.ALIGN_CENTER, font_color=(0,150,0), border_width=2, border_color=(0,150,0), background_color=self.green_button)
        define_exercise_ui.add.vertical_margin(30)
        button_cancel = define_exercise_ui.add.button('ANNULER', partial(quit_ui, False), background_color=self.yellow_button)
        define_exercise_ui.add.vertical_margin(5)
        button_cancel.set_font(pg_menu.font.FONT_NEVIS, 24, self.BLACK, self.WHITE, self.WHITE, self.WHITE, (255,255,255,0))
        button_save = define_exercise_ui.add.button('ENREGISTRER', partial(quit_ui, True), background_color=self.green_button)
        define_exercise_ui.add.vertical_margin(30)
        
        # Creation of the stages, whether fetching them from the DB or from scratch
        self.stored_stages = []
        if not is_new_exercise:
            stages_from_db = db.get_all_stages_from_ex(self.current_exercise)
            print("stages_from_db",stages_from_db)
            for stage in stages_from_db:
                self.stored_stages.append(dict(temps=stage[2], resistance=stage[3], difficulte=stage[4], vitesse=stage[5]))
            for i in range(0, len(self.stored_stages)):
                add_stage(self.stored_stages[i], False)
        else :
            for i in range(0, 3):
                add_stage(None, False)
        print("stored",self.stored_stages)
        # Declaration of the virtual keyboard
        layout = vkboard.VKeyboardLayout(vkboard.VKeyboardLayout.AZERTY)
        def on_key_event(text):
            name_exercise_input.set_value(text)
            if self.debug: print(name_exercise_input.get_value())
            return
        keyboard = vkboard.VKeyboard(define_exercise_ui,
                                    on_key_event,
                                    layout,
                                    renderer=vkboard.VKeyboardRenderer.DARK,
                                    show_text=False)

        # Declaration of gray filter
        gray_filter = pg.Surface((self.size_x,self.size_y))
        gray_filter.set_alpha(128)
        gray_filter.fill((100,100,100))

        while True:
            time_delta = self.clock.tick(60)/1000.0

            # Check if name input is selected
            if is_new_exercise:
                is_kb_active = name_exercise_input.get_selected_time() != 0
            else:
                is_kb_active = False

            # Doesn't allow an already existing name for the exercise
            if is_new_exercise and (name_exercise_input.get_value() == '' or name_exercise_input.get_value() in existing_names):
                is_save_active = False
                button_save.set_font(pg_menu.font.FONT_NEVIS, 28, self.WHITE, self.WHITE, self.WHITE, self.WHITE, (255,255,255,0))
                button_save.set_background_color(self.gray_button)
            else:
                is_save_active = True
                button_save.set_font(pg_menu.font.FONT_NEVIS, 28, self.WHITE, self.WHITE, self.WHITE, self.WHITE, (255,255,255,0))
                button_save.set_background_color(self.green_button)

            events = pg.event.get()

            # Event loop
            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit")
                    if self.synchro.locked():
                        self.synchro.release()
                    sys.exit()
                elif event.type == pg.FINGERDOWN:
                    # Avoid double event (FINGERDOWN and MOUSEDOWN) when using touchscreen
                    events.remove(event)

            # While the virtual keyboard is active, deactivates all widgets and displays a gray transparent filter
            if is_kb_active:
                for i in ids:
                    define_exercise_ui.get_widget('label'+str(i)).hide()
                    define_exercise_ui.get_widget('remove_button'+str(i)).hide()
                    define_exercise_ui.get_widget('label_temps'+str(i)).hide()
                    define_exercise_ui.get_widget('temps_m'+str(i)).hide()
                    define_exercise_ui.get_widget('temps_s'+str(i)).hide()
                    define_exercise_ui.get_widget('frame_temps'+str(i)).hide()
                    define_exercise_ui.get_widget('resistance'+str(i)).hide()
                    define_exercise_ui.get_widget('difficulte'+str(i)).hide()
                    define_exercise_ui.get_widget('vitesse'+str(i)).hide()
                define_exercise_ui.get_widget('add_stage_button').hide()
                if is_new_exercise: name_exercise_check.show()
                button_cancel.hide()
                button_save.hide()
            else:
                for i in ids:
                    define_exercise_ui.get_widget('label'+str(i)).show()
                    define_exercise_ui.get_widget('remove_button'+str(i)).show()
                    define_exercise_ui.get_widget('label_temps'+str(i)).show()
                    define_exercise_ui.get_widget('temps_m'+str(i)).show()
                    define_exercise_ui.get_widget('temps_s'+str(i)).show()
                    define_exercise_ui.get_widget('frame_temps'+str(i)).show()
                    define_exercise_ui.get_widget('resistance'+str(i)).show()
                    define_exercise_ui.get_widget('difficulte'+str(i)).show()
                    define_exercise_ui.get_widget('vitesse'+str(i)).show()
                define_exercise_ui.get_widget('add_stage_button').show()
                if is_new_exercise: name_exercise_check.hide()
                button_cancel.show()
                button_save.show()

            # Update display
            define_exercise_ui.draw(self.screen)
            
            if is_kb_active: 
                self.screen.blit(gray_filter, (0,0))
                rects = keyboard.draw(self.screen, True)
                frame.draw(self.screen)
                
            define_exercise_ui.update(events)
            if is_kb_active: keyboard.update(events)

            # Displays connection icon
            if self.connection_timeout > 0: self.screen.blit(self.connection_ok, (5,self.size_y-35))
            else:                           self.screen.blit(self.connection_failure, (5,self.size_y-35))
            self.connection_timeout = self.connection_timeout - 1

            # Displays user name in the bottom-right corner
            if not is_kb_active:
                user_name = pg.font.Font('freesansbold.ttf', 24).render(self.current_user, True, (255,255,255), None)
                user_name_rect = user_name.get_rect()
                user_name_rect.center = (self.screen.get_width()-user_name_rect.width/2-5,self.screen.get_height()-user_name_rect.height/2-5)
                self.screen.blit(user_name, user_name_rect)

            # Flip only the updated area
            pg.display.update()
            # Displays keyboard only if the name input is selected
            if is_kb_active: pg.display.update(rects)
    
    def _string_duration(self, secs_total):
        info_duration=''
        nb_minutes, nb_secs = divmod(secs_total, 60)
        if nb_minutes == 0:
            info_duration= str(int(nb_secs)) + 's'
        else:
            nb_hours, nb_minutes = divmod(nb_minutes, 60)
            if nb_hours > 0:
                info_duration = str(int(nb_hours)) + 'h' 
            info_duration = info_duration + str(int(nb_minutes)) + 'm' +  str(int(nb_secs)) + 's'

        return(info_duration)

    def display_stats_ui(self):
        """Displays information about the current user"""
        stats_ui = pg_menu.Menu('STATISTIQUES', self.size_x, self.size_y, theme=self.mytheme)

        # Get user data from database
        user_data = db.get_data_from_user(self.current_user)
        # String preparion to display duration in h/m/s
        duration_total = self._string_duration(user_data[2])
        duration_max = self._string_duration(user_data[3])
        
        # Statistics display
        image_total_time = stats_ui.add.image(self.icon_chrono)
        label_total_time = stats_ui.add.label('Temps total', font_color=(200,200,200), font_size=20)
        label_total_time_res=stats_ui.add.label(duration_total, font_color=self.WHITE, font_size=36)
        if self.orientation == 'portrait':
            frame_total_time = stats_ui.add.frame_v(250,250, background_color=self.wood_background)
        else:
            frame_total_time = stats_ui.add.frame_v(250,250)
        frame_total_time.pack(image_total_time, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame_total_time.pack(label_total_time, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame_total_time.pack(label_total_time_res, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)

        image_nb_games = stats_ui.add.image(self.icon_arrive)
        label_nb_games = stats_ui.add.label('Parties jouees', font_color=(200,200,200), font_size=20)
        label_nb_games_res = stats_ui.add.label(str(user_data[1]), font_color=self.WHITE, font_size=36)
        if self.orientation == 'portrait':
            frame_nb_games = stats_ui.add.frame_v(250,250, background_color=self.wood_background)
        else:
            frame_nb_games = stats_ui.add.frame_v(250,250)
        frame_nb_games.pack(image_nb_games, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame_nb_games.pack(label_nb_games, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame_nb_games.pack(label_nb_games_res, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)

        image_mean_speed = stats_ui.add.image(self.icon_snail)
        label_mean_speed = stats_ui.add.label('Vitesse moyenne', font_color=(200,200,200), font_size=20)
        label_mean_speed_res = stats_ui.add.label(str(round(user_data[0], 1)), font_color=self.WHITE, font_size=36)
        if self.orientation == 'portrait':
            frame_mean_speed = stats_ui.add.frame_v(250,250, background_color=self.wood_background)
        else:
            frame_mean_speed = stats_ui.add.frame_v(250,250)
        frame_mean_speed.pack(image_mean_speed, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame_mean_speed.pack(label_mean_speed, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame_mean_speed.pack(label_mean_speed_res, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)

        image_longest_game = stats_ui.add.image(self.icon_hourglass)
        label_longest_game = stats_ui.add.label('Plus longue partie', font_color=(200,200,200), font_size=20)
        label_longest_game_res = stats_ui.add.label(duration_max, font_color=self.WHITE, font_size=36)
        if self.orientation == 'portrait':
            frame_longest_game = stats_ui.add.frame_v(250,250, background_color=self.wood_background)
        else:
            frame_longest_game = stats_ui.add.frame_v(250,250)
        frame_longest_game.pack(image_longest_game, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame_longest_game.pack(label_longest_game, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame_longest_game.pack(label_longest_game_res, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)

        if self.orientation == 'portrait':
            frame_h1 = stats_ui.add.frame_h(540, 300)
            frame_h1.pack(frame_total_time, align=pg_menu.locals.ALIGN_LEFT)
            frame_h1.pack(frame_nb_games, align=pg_menu.locals.ALIGN_RIGHT)
            frame_h2 = stats_ui.add.frame_h(540, 300)
            frame_h2.pack(frame_mean_speed, align=pg_menu.locals.ALIGN_LEFT)
            frame_h2.pack(frame_longest_game, align=pg_menu.locals.ALIGN_RIGHT)
            frame_v = stats_ui.add.frame_v(600, 650)
            frame_v.pack(frame_h1, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
            frame_v.pack(frame_h2, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        else:
            frame_h = stats_ui.add.frame_h(self.size_x, frame_total_time.get_height() + 30, background_color=self.wood_background)
            frame_h.pack(frame_total_time)
            frame_h.pack(frame_nb_games)
            frame_h.pack(frame_mean_speed)
            frame_h.pack(frame_longest_game)

        stats_ui.add.vertical_margin(30)
        stats_ui.add.button('RETOUR', self.display_select_game_ui, background_color=self.yellow_button)


        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    if self.synchro.locked():
                        self.synchro.release()
                    sys.exit()

            stats_ui.update(events)

            stats_ui.draw(self.screen)

            # Displays connection icon
            if self.connection_timeout > 0: self.screen.blit(self.connection_ok, (5,self.size_y-35))
            else:                           self.screen.blit(self.connection_failure, (5,self.size_y-35))
            self.connection_timeout = self.connection_timeout - 1

            user_name = pg.font.Font('freesansbold.ttf', 24).render(self.current_user, True, (255,255,255), None)
            user_name_rect = user_name.get_rect()
            user_name_rect.center = (self.screen.get_width()-user_name_rect.width/2-5,self.screen.get_height()-user_name_rect.height/2-5)
            self.screen.blit(user_name, user_name_rect)
            
            pg.display.update()


    def display_delete_user_ui(self):
        """Displays a confirmation before deleting the requested user"""

        def delete_user():
            db.delete_user(self.current_user)
            self.current_user = 'everybody'
            self.display_select_user_ui()

        delete_user_ui = pg_menu.Menu('SUPPRIMER UN UTILISATEUR', self.size_x, self.size_y, theme=self.mytheme)

        confirm_frame = delete_user_ui.add.frame_v(400,200, background_color=self.stone_background)
        confirm_label = delete_user_ui.add.label('Etes-vous sur de vouloir\nsupprimer le joueur suivant ?', font_color=(220,220,220), font_size=24)
        confirm_user  = delete_user_ui.add.label(self.current_user, font_color=self.WHITE, font_size=40, background_color=self.jewel_background)
        confirm_frame.pack(confirm_label, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        confirm_frame.pack(confirm_user,  align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        delete_user_ui.add.vertical_margin(15)
        delete_user_ui.add.button('SUPPRIMER', delete_user, background_color=self.red_button)
        delete_user_ui.add.vertical_margin(15)
        delete_user_ui.add.button('ANNULER', self.display_select_user_ui, background_color=self.yellow_button)

        while True:
            time_delta = self.clock.tick(60)/1000.0
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    if self.synchro.locked():
                        self.synchro.release()
                    sys.exit()

            delete_user_ui.update(events)

            delete_user_ui.draw(self.screen)

            # Displays connection icon
            if self.connection_timeout > 0: self.screen.blit(self.connection_ok, (5,self.size_y-35))
            else:                           self.screen.blit(self.connection_failure, (5,self.size_y-35))
            self.connection_timeout = self.connection_timeout - 1
            
            pg.display.update()

        
    def display_create_user_ui(self):
        """ Displays the user creation ui """

        def create_user(name_input):
            """ Add the new user in the database and displays game selection ui
        
            Args:
                name_input (string): name of the new user
            """
            if is_save_active:
                name = name_input.get_value()
                db.create_new_user(name)
                self.current_user = name
                self.display_select_game_ui()
            else:
                if self.debug: print("User name is empty or already exists in the database")
                return

        create_user_ui = pg_menu.Menu('NOUVEL UTILISATEUR', self.size_x, self.size_y, theme=self.mytheme)
        name_label = create_user_ui.add.label("NOM")
        name_input = create_user_ui.add.text_input('', maxwidth=300, maxchar=20)
        name_check = create_user_ui.add.button('OK', background_color=self.green_button, font_size=20)

        frame = create_user_ui.add.frame_v(400, name_label.get_height() + name_input.get_height() + name_check.get_height() + 30, background_color=self.stone_background)
        frame.pack(name_label, align=pg_menu.locals.ALIGN_CENTER)
        frame.pack(name_input, align=pg_menu.locals.ALIGN_CENTER)
        frame.pack(create_user_ui.add.vertical_margin(10))
        frame.pack(name_check, align=pg_menu.locals.ALIGN_CENTER)
        create_user_ui.add.vertical_margin(50)
        button_save = create_user_ui.add.button('VALIDER', action=partial(create_user, name_input), background_color=self.green_button)
        create_user_ui.add.vertical_margin(70)
        create_user_ui.add.button('ANNULER', self.display_select_user_ui, background_color=self.yellow_button)
        
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

            # Doesn't allow an already existing name
            if name_input.get_value() == '' or name_input.get_value() in existing_names:
                is_save_active = False
                button_save.set_font(pg_menu.font.FONT_NEVIS, 28, self.WHITE, self.WHITE, self.WHITE, self.WHITE, (255,255,255,0))
                button_save.set_background_color(self.gray_button)
            else:
                is_save_active = True
                button_save.set_font(pg_menu.font.FONT_NEVIS, 28, self.WHITE, self.WHITE, self.WHITE, self.WHITE, (255,255,255,0))
                button_save.set_background_color(self.green_button)

            for event in events:
                if event.type == pg.QUIT:
                    pg.display.quit()
                    if self.debug: print("Quit") 
                    if self.synchro.locked():
                        self.synchro.release()
                    sys.exit()
                elif event.type == pg.FINGERDOWN:
                    #Avoid double event (FINGERDOWN and MOUSEDOWN) when using touchscreen
                    events.remove(event)

            create_user_ui.update(events)
            if name_input.get_selected_time() != 0: keyboard.update(events)
            create_user_ui.draw(self.screen)
            # Displays keyboard only when input is selected
            if name_input.get_selected_time() != 0: rects = keyboard.draw(self.screen, True)

            # Displays connection icon
            if self.connection_timeout > 0: self.screen.blit(self.connection_ok, (5,self.size_y-35))
            else:                           self.screen.blit(self.connection_failure, (5,self.size_y-35))
            self.connection_timeout = self.connection_timeout - 1
            
            # Flip only the updated area
            pg.display.update()
            if name_input.get_selected_time() != 0: pg.display.update(rects)
    
 
    def display_score_ui(self, duration, time_paused, distance, score):
        """ Opens score_ui """
        if len(self.speed_values) > 0:  
            mean_global = int(statistics.mean(self.speed_values))
        else:                           
            mean_global = 0.0
            
        mean_global

        # Update database
        if not self.demo_mode: db.update_data_from_user(self.current_user, mean_global, duration)
        
        score_ui = pg_menu.Menu('FELICITATIONS!', self.size_x, self.size_y, theme=self.mytheme)
        minutes, seconds = divmod(duration, 60)
        label_duration = score_ui.add.label("Time : " + str(int(minutes)) + "'" + str(int(seconds)) + "\"", font_color=self.WHITE)
        minutes, seconds = divmod(time_paused, 60)
        label_pause = score_ui.add.label("Pause : " + str(int(minutes)) + "'" + str(int(seconds)) + "\"", font_color=(230,230,230), font_size=20)
        label_distance = score_ui.add.label("Distance : " + str(round(distance)), font_color=self.WHITE)
        label_score = score_ui.add.label("Score : " + str(round(score)), font_color=self.WHITE)
        label_vitessemoy = score_ui.add.label("Vitesse moyenne : " + str(round(mean_global, 2)), font_color=self.WHITE)
        frame = score_ui.add.frame_v(400, label_duration.get_height() * 5 + 30, background_color=self.stone_background)
        frame.pack(label_duration, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame.pack(label_pause, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame.pack(label_distance, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame.pack(label_score, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        frame.pack(label_vitessemoy, align=pg_menu.locals.ALIGN_CENTER, vertical_position=pg_menu.locals.POSITION_CENTER)
        score_ui.add.vertical_margin(30)
        score_ui.add.button('REJOUER', partial(self.launch_selected_game, self.demo_mode, self.kb_input), background_color=self.green_button)
        score_ui.add.vertical_margin(30)
        if self.demo_mode:  score_ui.add.button('MENU', partial(self.display_select_difficulty_ui), background_color=self.yellow_button)
        else :              score_ui.add.button('MENU', partial(self.display_select_game_ui), background_color=self.yellow_button)
        score_ui.add.vertical_margin(30)
        score_ui.add.button('QUITTER', pg_menu.events.EXIT, background_color=self.red_button)

        while True:
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT: 
                    pg.display.quit()
                    if self.debug : print("Quit") 
                    if self.synchro.locked():
                        self.synchro.release()
                    if self.wind_resistor != None:
                        self.wind_resistor.stop()
                    sys.exit()

            if score_ui.is_enabled():
                score_ui.update(events)
                score_ui.draw(self.screen)

            # Displays connection icon
            if self.connection_timeout > 0: self.screen.blit(self.connection_ok, (5,self.size_y-35))
            else:                           self.screen.blit(self.connection_failure, (5,self.size_y-35))
            self.connection_timeout = self.connection_timeout - 1

            user_name = pg.font.Font('freesansbold.ttf', 24).render(self.current_user, True, (255,255,255), None)
            user_name_rect = user_name.get_rect()
            user_name_rect.center = (self.screen.get_width()-user_name_rect.width/2-5,self.screen.get_height()-user_name_rect.height/2-5)
            self.screen.blit(user_name, user_name_rect)
            
            pg.display.update()


    def message_callback(self, client, userdata, message):
        """ executes the function corresponding to the called topic """

        if message.topic == "fit_and_fun/current_stage":
            if not self.kb_input:
                self.get_speed(client, userdata, message)
        elif message.topic == "fit_and_fun/speed_kb":
            if self.kb_input:
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
            elif rot_speed > self.ROT_SPEED_MAX:
                self.rot_speed=self.ROT_SPEED_MAX
            else:
                self.rot_speed=rot_speed
        except Exception:
            self.rot_speed=0
        print('rot_speed',self.rot_speed)


        self.connection_timeout = self.TIMEOUT_TOLERANCE

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
