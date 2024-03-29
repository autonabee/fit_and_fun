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
from console import Console
from game_canoe import GameCanoe
import threading


class KeyboardController():
    
    def __init__(self, on_message):
        self.on_message = on_message
        self.lock = threading.Lock()
        self.lock.acquire()
    
    def run(self):
        self.t1 = threading.Thread(target=self.kb_input_process, daemon=True)
        self.t1.start()
    
    class FakeMQTTMessage():
        def __init__(self, payload):
            self.payload = payload.encode("utf-8")
        
        def __str__(self):
            return self.payload.decode("utf-8")
    
    def kb_input_process(self):
        state = 0    # state == 1 if a key is pressed
        n_press = 0
        last_ticks = pg.time.get_ticks()
        timer = 0
        virtual_speed = 0
        while True:
            if pg.key.get_focused():
                keys = pg.key.get_pressed()
                if state == 0 and keys[pg.K_UP]:
                    state = 1
                    n_press += 1
                elif state == 1 and not keys[pg.K_UP]:
                    state = 0
            
            current_ticks = pg.time.get_ticks()
            dt = current_ticks - last_ticks
            timer += dt
            last_ticks = current_ticks
            
            # Send the value every 100 millisec to simulate the real sensor's frequency
            if timer > 100:
                virtual_speed = min(max(0, virtual_speed - 1.5), 15)
                virtual_speed += n_press * 4
                message = self.FakeMQTTMessage(str(virtual_speed))
                self.on_message(None, None, message)
                n_press = 0
                timer = 0
            
    def stop(self):
        self.lock.release()
        self.t1.join()



console = GameCanoe()
virtualController = KeyboardController(console.get_speed)
virtualController.run()
console.display_select_user_ui()
