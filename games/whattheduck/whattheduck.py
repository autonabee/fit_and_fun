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

"""
    Projet Fit & Fun
    Autonabee

    Fabrikarium 2022 à Rennes
    code: Gweltaz Duval-Guennoc, Les Portes Logiques, Quimper
    contact: gweltou@hotmail.com
"""


import pygame as pg
import pygame_menu as pg_menu
import time
import os
import sys
import random
import statistics
from console import Console
from game_entities import Player, Obstacle, Bonus, LandscapeProp
from game_events import start_events, event_blocks


class Stage:
    def __init__(
        self,
        # unique exercice id
        name: str,
        # in seconds
        duration,
        temps: int,
        resistance: float,
        difficulty: int,
    ):
        self.name = name
        self.duration = duration
        self.temps = temps
        self.resistance = resistance
        self.difficulty = difficulty


class GameCanoe:
    # Images
    dir_img = os.path.join(os.path.dirname(__file__), "images")
    heart_full_img = pg.image.load(dir_img + "/heart_full.png")
    heart_empty_img = pg.image.load(dir_img + "/heart_empty.png")

    # Constants
    SCROLL_SPEED_MAX = 0.2  # Raise value for a faster river current
    SCROLL_SPEED_MIN = 0.02  # Minimum current speed of the river
    SPEED_SMOOTHING = 0.8  # To smooth speed value and avoid jagginess, between 0 and 1
    BONUS_DURATION = (
        2.0  # Duration of speed bonus with doubled scrolling speed (in seconds)
    )
    BONUS_COOLDOWN = 1.0  # Speed bonus deceleration period (in seconds)
    SCORE_RATIO = 0.02  # Ratio between effective speed and apparent score

    def __init__(self, console: Console, stages: list[Stage]):
        self.console = console
        self.screen = console.screen

        # Time init
        self.clock = pg.time.Clock()
        self.time0 = time.time()

        # Loading sprite assets
        if console.orientation == "portrait":
            self.river_bg = pg.image.load(self.dir_img + "/level_bg_portrait.png")
        else:
            self.river_bg = pg.image.load(self.dir_img + "/level_bg_landscape.png")
        self.duck_sprites = [
            pg.image.load(os.path.join(self.dir_img, f"canard_{i}.png"))
            for i in range(1, 3)
        ]
        self.bush_sprites = [
            pg.image.load(os.path.join(self.dir_img, f"buisson_{i}.png"))
            for i in range(1, 3)
        ]
        self.tree_sprites = [
            pg.image.load(os.path.join(self.dir_img, f"tree_{i}.png"))
            for i in range(1, 3)
        ]
        self.rock_sprites = [
            pg.image.load(os.path.join(self.dir_img, f"rocher_{i}.png"))
            for i in range(1, 4)
        ]
        self.trunc_sprites = [
            pg.image.load(os.path.join(self.dir_img, f"wood_{i}.png"))
            for i in range(1, 3)
        ]

        # Assets augmentation
        duck_sprites_aug = []
        for s in self.duck_sprites:
            # Resized and mirrored
            # resized = pg.transform.rotozoom(s, 0, 1.25)
            flipped = pg.transform.flip(s, True, False)
            duck_sprites_aug.append(s)
            duck_sprites_aug.append(flipped)
        self.duck_sprites = duck_sprites_aug
        for elt in self.rock_sprites[:]:
            # Smaller rocks
            self.rock_sprites.append(pg.transform.scale(elt, (0.5, 0.5)))
        for elt in self.rock_sprites[:]:
            # Vertically flipped rocks
            self.rock_sprites.append(pg.transform.flip(elt, False, True))
        for elt in self.trunc_sprites[:]:
            # Smaller tree truncs
            self.trunc_sprites.append(pg.transform.scale(elt, (0.5, 0.5)))
        # Rotate all tree truncs
        self.trunc_sprites = [
            pg.transform.rotate(ws, random.choice([75, -70, 60, -50]))
            for ws in self.trunc_sprites
        ]

        # Data
        self.previous_speed = 0  # Used for value smoothing
        self.bg_y = 0
        self.bonus_timer = 0
        distance = 0  # Virtual rowing distance (in bogo-meters)
        self.level_started = False
        control_enabled = True
        self.fixed_speed = 0
        self.score = 0.0
        self.life_count = 3

        # Exercise stages
        self.stages = []
        for stage in stages:
            self.stages.append(stage)
        self.current_stage : Stage = self.stages[0]
        self.speed_vals_cstage = []

        # Entities are instanciated once to avoid garbage collection as much as possible
        self.player = Player(self.screen, self.dir_img)
        self.bonus = Bonus(self.screen, self.dir_img)  # Only one bonus at each moment
        self.obstacles = [Obstacle(self.screen) for _ in range(32)]
        self.landscape = [LandscapeProp(self.screen) for _ in range(16)]
        self.special_scenery = [LandscapeProp(self.screen) for _ in range(8)]

        # Level events
        # game_events is initialized with the game's basic events (3,2,1,GO)
        self.game_events = start_events.copy()
        self.timebegin = 0
        self.timebegin_game = 0

        self.is_game_paused = False
        self.time_paused = 0.0

        self.is_game_started = False

        self.game_events.sort(key=lambda x: x[0])  # Sort by time

        # Init pause menu, which is only displayed when the game is paused
        def resume():
            """Resume game when in pause menu"""
            self.is_game_paused = False

        def forfeit():
            """Stops game when in pause menu and displays score UI"""
            self.console.display_score_ui(
                time.time() - self.timebegin - self.time_paused,
                self.time_paused,
                distance,
                self.score,
            )

        mytheme = pg_menu.Theme(
            title_bar_style=pg_menu.widgets.MENUBAR_STYLE_NONE,
            background_color=(0, 0, 0, 0),
        )
        mytheme.widget_font = pg_menu.font.FONT_NEVIS
        self.pause_ui = pg_menu.Menu("", console.size_x, console.size_y, theme=mytheme)
        self.pause_ui.add.label(
            "PAUSE",
            font_color=console.WHITE,
            background_color=console.stone_background,
            padding=(10, 40, 10, 40),
        )
        self.pause_ui.add.vertical_margin(50)
        self.pause_ui.add.button(
            "REPRENDRE", resume, background_color=console.green_button
        )
        self.pause_ui.add.vertical_margin(50)
        self.pause_ui.add.button(
            "ABANDONNER", forfeit, background_color=console.red_button
        )

    def draw_text(self, text, size, x, y):
        """Print text on the panel with

         Parameters
        ----------
            size: int
                size of the text
            x: int
                x location of the text
            y: int
                y location of the text
        """
        font = pg.font.Font(self.console.font_name, size)
        text_surface = font.render(text, True, self.console.BLACK)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_life(self):
        """Print life counter in the top left corner with

         Parameters
        ----------
            life_counter: int
                number of remaining lives
        """
        self.screen.blit(self.heart_full_img, (5, 30))
        if self.life_count >= 2:
            self.screen.blit(self.heart_full_img, (5, 61))
        else:
            self.screen.blit(self.heart_empty_img, (5, 61))
        if self.life_count == 3:
            self.screen.blit(self.heart_full_img, (5, 92))
        else:
            self.screen.blit(self.heart_empty_img, (5, 92))

    def get_banner(self):
        """Format textual information

        Return
        ------
        banner: string
         contains time, speed and score
        """
        # Timer activates only when the game begins
        if self.timebegin == 0:
            minutes, seconds = divmod(self.current_stage.duration, 60)
            self.console.speed_values = []
            self.speed_vals_sec = []
            self.cseconds = int(seconds)
            self.cstage = self.current_stage.name
        else:
            duration = time.time() - self.timebegin - self.time_paused
            minutes, seconds = divmod(self.current_stage.duration + 1 - duration, 60)
            self.speed_vals_sec.append(self.console.rot_speed)
            # Store the mean of all registered speed values each second
            if self.cseconds != int(seconds):
                if len(self.speed_vals_sec) > 0:
                    mean_vel = statistics.mean(self.speed_vals_sec)
                    self.console.speed_values.append(int(mean_vel))
                    self.speed_vals_sec = []
                self.cseconds = int(seconds)

        template = "Etape {etape}/{max_etape:01d} - Time: {min:02d}:{sec:02d} - Speed: {speed:03d} - Score: {score:03d}"
        banner = template.format(
            etape=self.current_stage.name,
            max_etape=len(self.stages),
            min=int(minutes),
            sec=int(seconds),
            speed=int(self.console.rot_speed),
            score=round(self.score),
        )
        return banner

    def flush_events_queue(self):
        """Empties the event queue and re-fill it with new randomly generated events"""
        self.game_events.clear()
        while len(self.game_events) <= 10:
            delay = (
                time.time()
                - self.time0
                - self.time_paused
                + random.randint(
                    30 - 2 * self.current_stage.resistance, 32 - 2 * self.current_stage.resistance
                )
            )  # Values can be changed to in/decrease spawn rate
            ev_block = random.choice(list(event_blocks.values()))
            events = [(delay + te, *ev) for te, *ev in ev_block["events"]]
            self.game_events.extend(events)
            self.game_events.sort(key=lambda x: x[0])  # Sort by time

    def game(self):
        """
        game panel. A character go headed on a scrolled side game depending
        on its speed. If it reaches muschroom the score is decrease.
        """

        # Initial time when the game begins
        self.time0 = time.time()

        while True:
            time_delta = self.clock.tick(30)

            if not self.is_game_paused:

                ####  Scripted Game Events (see file game_events.py)  ####
                if len(self.game_events) > 0:
                    t = time.time() - self.time0 - self.time_paused
                    if self.game_events[0][0] < t:
                        event_type = self.game_events[0][1]
                        if event_type == "LOCK":  # Lock game control
                            control_enabled = False
                        elif event_type == "UNLOCK":  # Enable game control
                            control_enabled = True
                        elif event_type == "FS":  # Fixed speed
                            event_data = self.game_events[0][2]
                            self.fixed_speed = event_data
                        elif (
                            event_type == "LVL_START"
                        ):  # Start level (obstacles, bonuses and score recording)
                            self.level_started = True
                            self.timebegin = time.time()
                            self.timebegin_game = time.time()
                            self.is_game_started = True
                        elif event_type == "DECO":  # Spawn special scenery
                            event_data = self.game_events[0][2]
                            for elt in self.special_scenery:
                                if not elt.alive:
                                    sprite_filename = os.path.join(
                                        self.dir_img, event_data[0]
                                    )
                                    sprite = pg.image.load(sprite_filename)
                                    elt.spawn(sprite, 0)
                                    elt.pos_x = (
                                        self.console.size_x * 0.5 + event_data[1]
                                    )
                                    break
                            else:
                                print("WARNING: special_scenery array is full")
                        elif event_type == "BONUS":
                            h = self.game_events[0][2]
                            bonus_height = self.console.size_y * (1.0 - h)
                            self.bonus.spawn(bonus_height)
                        elif event_type == "OBS_duck":
                            indiv, h, dir, speed = self.game_events[0][2]
                            for obs in self.obstacles:
                                if not obs.alive:
                                    side = dir
                                    if side >= 0:
                                        sprite = self.duck_sprites[
                                            indiv * 2 + 0
                                        ]  # facing right
                                    else:
                                        sprite = self.duck_sprites[
                                            indiv * 2 + 1
                                        ]  # facing left

                                    spawn_height = self.console.size_y * (1.0 - h)
                                    obs.spawn(sprite, spawn_height, side, speed)
                                    break
                            else:
                                print("WARNING: obstacle array is full")
                        else:
                            print(
                                "ERROR: event type '{}' not found in event_blocks".format(
                                    event_type
                                )
                            )

                        # Remove the oldest event and add a new one
                        del self.game_events[0]
                        delay = (
                            time.time()
                            - self.time0
                            - self.time_paused
                            + random.randint(
                                30 - 2 * self.current_stage.resistance,
                                32 - 2 * self.current_stage.resistance,
                            )
                        )  # Values can be changed to in/decrease spawn rate
                        if len(self.game_events) <= 10 and self.is_game_started:
                            ev_block = random.choice(list(event_blocks.values()))
                            events = [
                                (delay + te, *ev) for te, *ev in ev_block["events"]
                            ]
                            self.game_events.extend(events)
                            self.game_events.sort(key=lambda x: x[0])  # Sort by time

                # Normalizing and smoothing speed value
                if control_enabled:
                    if pg.joystick.get_count() > 0:
                        print("joy")
                        joy = pg.joystick.Joystick(0)
                        if not joy.get_init(): joy.init()
                        self.console.rot_speed = joy.get_axis(0)
                    else:
                        print("nojoy")
                        self.console.rot_speed = 10.0 if pg.key.get_pressed()[pg.K_UP] else 0.0
                    rot_speed_normalized = (
                        self.console.rot_speed / self.console.ROT_SPEED_MAX
                    )
                else:
                    rot_speed_normalized = 0
                speed = (
                    self.SPEED_SMOOTHING * self.previous_speed
                    + (1 - self.SPEED_SMOOTHING) * rot_speed_normalized
                )
                self.previous_speed = speed
                self.player.speed = speed  # speed is normalized (between 0 and 1)

                # Increase score
                self.score = self.score + self.console.rot_speed * self.SCORE_RATIO

                ####  Speed Bonus  ####
                if self.bonus_timer > 0:
                    # Bonus is activated
                    if self.bonus_timer > self.BONUS_COOLDOWN * 1000:
                        # Full speed
                        scroll_speed = 2 * self.SCROLL_SPEED_MAX
                    else:
                        # Decelerating by interpolating between double speed and regular speed
                        a = self.bonus_timer / (self.BONUS_COOLDOWN * 1000)
                        scroll_speed = a * 2 * self.SCROLL_SPEED_MAX + (1 - a) * (
                            self.SCROLL_SPEED_MAX * speed + self.SCROLL_SPEED_MIN
                        )
                    self.bonus_timer -= time_delta
                else:
                    scroll_speed = self.SCROLL_SPEED_MAX * speed + self.SCROLL_SPEED_MIN

                if self.fixed_speed > 0:
                    scroll_speed = self.fixed_speed * self.SCROLL_SPEED_MAX

                if self.level_started:
                    distance += scroll_speed * time_delta * 0.01
                else:
                    distance = 0

                ####  Background scrolling  ####
                self.screen.blit(self.river_bg, (0, self.bg_y - self.console.size_y))
                self.screen.blit(self.river_bg, (0, self.bg_y))
                self.screen.blit(self.river_bg, (0, self.bg_y + self.console.size_y))
                # The scrolling speed depends on the player speed
                self.bg_y = self.bg_y + scroll_speed * time_delta
                if self.bg_y >= self.console.size_y:
                    self.bg_y = 0

                ####  Update all entities  ####
                self.player.update(time_delta)
                self.bonus.update(time_delta)

                for elt in self.landscape:
                    elt.update(time_delta, scroll_speed)

                for elt in self.special_scenery:
                    elt.update(time_delta, scroll_speed)

                for obs in self.obstacles:
                    obs.update(time_delta)

                ####  Obstacle/Player collision detection  ####
                colliding = self.player.hitbox.collidelistall(
                    [o.hitbox for o in self.obstacles if o.alive]
                )
                if len(colliding) > 0:
                    was_hit = self.player.hit()
                    if was_hit:
                        self.score -= 100
                        self.life_count -= 1
                for i in colliding:
                    self.obstacles[i].alive = False

                if self.bonus.alive and self.player.hitbox.colliderect(
                    self.bonus.hitbox
                ):
                    self.bonus.alive = False
                    self.bonus_timer = (
                        self.BONUS_DURATION + self.BONUS_COOLDOWN
                    ) * 1000
                    self.score += 100

                for elt in self.special_scenery:
                    elt.draw()

                # Draw landscape elements in order defined by their layer
                self.landscape.sort(key=lambda x: x.layer)
                for elt in self.landscape:
                    elt.draw()

                self.bonus.draw()
                self.player.draw()

                for obs in self.obstacles:
                    obs.draw()

                ####  Spawning Lanscape elements  ####
                if random.random() < 0.05:
                    # Spawn rocks on bottom layer
                    for elt in self.landscape:
                        if not elt.alive:
                            elt.spawn(random.choice(self.rock_sprites), 0)
                            break
                if random.random() < 0.01:
                    # Spawn tree truncs
                    for elt in self.landscape:
                        if not elt.alive:
                            elt.spawn(
                                random.choice(self.bush_sprites + self.trunc_sprites), 1
                            )
                            break
                if random.random() < 0.01:
                    # Spawn bushes
                    for elt in self.landscape:
                        if not elt.alive:
                            elt.spawn(random.choice(self.bush_sprites), 2)
                            break
                if random.random() < 0.01:
                    # Spawn trees on highest layer
                    for elt in self.landscape:
                        if not elt.alive:
                            elt.spawn(random.choice(self.tree_sprites), 3)
                            break

                ####  HUD  ####
                self.draw_text(self.get_banner(), 25, self.console.size_x / 2, 1)
                self.draw_text(
                    str(round(distance, 1)),
                    25,
                    self.console.size_x - 32,
                    self.console.size_y - 32,
                )
                if self.console.demo_mode:
                    self.draw_life()

                if self.console.connection_timeout > 0:
                    self.screen.blit(
                        self.console.connection_ok, (5, self.console.size_y - 35)
                    )
                else:
                    self.screen.blit(
                        self.console.connection_failure, (5, self.console.size_y - 35)
                    )

                pg.display.update()

                self.console.connection_timeout = self.console.connection_timeout - 1

                # Check if the player is dead or if the time is elapsed
                time_elapsed_game = time.time() - self.timebegin_game - self.time_paused
                time_elapsed = time.time() - self.timebegin - self.time_paused

                if self.is_game_started:
                    if time_elapsed >= self.current_stage.duration:
                        index_current_stage = self.stages.index(self.current_stage)
                        if index_current_stage < len(self.stages) - 1:
                            self.current_stage = self.stages[index_current_stage + 1]
                            self.timebegin = time.time()
                            self.flush_events_queue()
                        else:
                            self.console.display_score_ui(
                                time_elapsed_game,
                                self.time_paused,
                                distance,
                                self.score,
                            )

                if self.console.demo_mode and self.life_count <= 0:
                    self.console.display_score_ui(
                        time_elapsed, self.time_paused, distance, self.score
                    )

            else:
                # If the game is paused, displays pause UI
                self.time_paused = self.time_paused + time_delta / 1000

                events = pg.event.get()
                self.pause_ui.update(events)

                self.pause_ui.draw(self.screen)
                pg.display.update()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    if not self.is_game_started:
                        self.console.display_score_ui(0, 0, distance, 0)
                    else:
                        self.console.display_score_ui(
                            time.time() - self.timebegin - self.time_paused,
                            self.time_paused,
                            distance,
                            self.score,
                        )
                elif event.type == pg.MOUSEBUTTONDOWN and self.is_game_started:
                    # Toggle pause UI
                    if not self.is_game_paused:
                        self.is_game_paused = True
                        pause_filter = pg.Surface(
                            (self.console.size_x, self.console.size_y)
                        )
                        pause_filter.set_alpha(128)
                        pause_filter.fill((100, 100, 100))
                        self.screen.blit(pause_filter, (0, 0))


if __name__ == "__main__":
    print("launching example game")
    g = GameCanoe(Console(), [Stage("Example", 120, 5, 1, 1)])
    g.game()
