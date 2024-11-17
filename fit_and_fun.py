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
from mqtt_subscriber import mqtt_subscriber
import threading
import subprocess
from subprocess import Popen
import tkinter as tk
from game import Game

__GAMES__ : list[Game] = [
    Game("print game", "games/print_game_launcher.py", lambda msg: print(f"msg: {msg}"))
]


def game_menu():
    root = tk.Tk()
    root.geometry("600x600")
    
    tk.Label(root, font=80, text="select a game").pack()
    for game in __GAMES__:
        print(game.name)
        def target():
            mqtt_subscriber(game.driver, threading.Lock(), 'fit_and_fun/speed')
            p = Popen(game.path)
            reload = True
            root.destroy()
            p.wait()
            game_menu()
            

        tk.Button(root, font=80, text="GAME: "+game.name, command=target).pack(pady=10)

    root.mainloop()


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
   
    if ARGS.orientation == 'landscape':
        process = subprocess.call('./orientation_landscape.sh')
    else:
        process = subprocess.call('./orientation_portrait.sh')
    
    game_menu()
