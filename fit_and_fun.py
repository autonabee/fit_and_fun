# This file is a part of Fit & Fun
#
# Copyright (C) 2023 Inria/Autonabee
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.ce-cill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

import argparse
from console import Console
from mqtt_subscriber import mqtt_subscriber
from wind import wind
import pygame as pg
import threading
import subprocess
import sys

# Input simulation via keyboard
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
            self.topic = "fit_and_fun/speed_kb"
            self.payload = payload.encode("utf-8")
        
        def __str__(self):
            return self.payload.decode("utf-8")
    
    def kb_input_process(self):
        state = 0    # state == 1 if a key is pressed
        n_press = 0
        last_ticks = pg.time.get_ticks()
        timer = 0
        virtual_speed = 0
        while pg.display.get_init():
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


# Main
if __name__ == "__main__":
    """Launch the game"""
    PARSER = argparse.ArgumentParser(
        description='Fit and fun game during sport') 
    PARSER.add_argument('-b', '--broker', dest='broker',
                        help='Broker host to connect (default localhost)', default='localhost')
    PARSER.add_argument('-w', '--wind', dest='wind', action='store_true',
                        help='Wind simulation resistance')
    PARSER.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='Display some additional informations')
    PARSER.add_argument('-f', '--fullscreen', dest='fullscreen', action='store_true',
                        help='Fullscreen mode')
    PARSER.add_argument('-c', '--controls', dest='controls', action='store_true',
                        help='Activates button controling')
    PARSER.add_argument('-l', '--local', dest='local', action='store_true',
                        help='Doesn\'t make the connection with MQTT broker')
    PARSER.add_argument('-o', '--orientation', dest='orientation',
                        help='Screen orientation (landscape or portrait)', default='portrait')
    ARGS = PARSER.parse_args()

    if ARGS.orientation != 'landscape' and ARGS.orientation != 'portrait':
        raise Exception("ERROR : property '" + ARGS.orientation + "' doesn't exist, accepted values are 'landscape' and 'portrait'")
   
    try:
   
        if ARGS.orientation == 'landscape':
            process = subprocess.call('./orientation_landscape.sh')
        else:
            process = subprocess.call('./orientation_portrait.sh')
        wind_resistor=None
        if ARGS.wind==True:
            wind_resistor=wind()
            wind_resistor.run()
        console=Console(ARGS.wind, ARGS.debug, ARGS.fullscreen, ARGS.orientation)
        subscribes = ['fit_and_fun/speed']
        if ARGS.controls:
            subscribes += ['fit_and_fun/select','fit_and_fun/down']
        if not ARGS.local:
            mqtt_sub=mqtt_subscriber(console.message_callback, console.synchro, subscribes, 
                                    broker_addr=ARGS.broker)
            mqtt_sub.run()
        virtualController = KeyboardController(console.message_callback)
        virtualController.run()
        # TODO: verify database is initiated
        console.display_select_user_ui()

    except KeyboardInterrupt:
        # quit
        virtualController.stop()
        sys.exit()

 