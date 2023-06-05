import pygame as pg
import pygame_menu as pg_menu
import time
import os
import math

class GameData():

    def __init__(self, console, stages):
        # Necessary variables in order to retrieve console data
        self.console = console
        self.screen = console.screen

    def game(self):

        # Constants
        SPEED_SMOOTHING = 0.8       # To smooth speed value and avoid jagginess, between 0 and 1
        COEFF_DISTANCE = 0.12       # Length of a pedal (m) - used to convert rad/s to m/s

        # Data
        previous_speed = 0  # Used for value smoothing
        distance = 0

        # Time init
        clock = pg.time.Clock()
        self.time0=time.time()

        # Interface creation
        mytheme = pg_menu.Theme(title_bar_style=pg_menu.widgets.MENUBAR_STYLE_NONE, background_color=(0,0,0))
        mytheme.widget_font=pg_menu.font.FONT_NEVIS
        game_ui = pg_menu.Menu('', self.console.size_x, self.console.size_y, theme=mytheme)
        time_label = game_ui.add.label('Temps : 0.0s', font_color=self.console.WHITE, background_color=self.console.stone_background)
        game_ui.add.vertical_margin(50)
        speed_label = game_ui.add.label('Vitesse : 0.0m/s', font_color=self.console.WHITE, font_size=32, background_color=self.console.stone_background)
        game_ui.add.vertical_margin(50)
        distance_label = game_ui.add.label('Distance : 0.0m', font_color=self.console.WHITE, background_color=self.console.stone_background)

        while True:
            time_delta = clock.tick(30)
            t = time.time() - self.time0

            # Normalizing and smoothing speed value
            rot_speed_normalized = self.console.rot_speed * COEFF_DISTANCE
            speed = SPEED_SMOOTHING * previous_speed + (1 - SPEED_SMOOTHING) * rot_speed_normalized
            previous_speed = speed
            distance = distance + speed / time_delta

            time_label.set_title('Temps : ' + str(round(t,1)) + 's')
            speed_label.set_title('Vitesse : ' + str(round(speed,1)) + 'm/s')
            distance_label.set_title('Distance : ' + str(round(distance,1)) + 'm')

            # Connexion status display
            if self.console.connection_timeout > 0: self.screen.blit(self.console.connection_ok, (5,self.size_y-35))
            else:                           self.screen.blit(self.console.connection_failure, (5,self.size_y-35))
            pg.display.update()
            self.console.connection_timeout = self.console.connection_timeout - 1

            # Events management
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.console.display_score_ui(time.time() - self.time0, 0, distance, 0)

            game_ui.update(events)

            game_ui.draw(self.screen)