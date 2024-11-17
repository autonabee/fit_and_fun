import pathlib
from subprocess import Popen

class Game(object):
    """
    A game compatible with the fit_and_fun hardware.

    exec_name : the name of the game

    exec_path : path to the game

    driver    : A function that accepts a MQTT message and converts it to inputs for the game, most likely using uinput or pynput.
    """
    def __init__(self, name : str, path : str, driver):
        # p = pathlib.Path(path)
        # if not p.exists() or not p.is_file():
        #     raise RuntimeError(f"Path doesn't point to a file: '{path}' for game : '{name}'")
        # if name == "":
        #     raise RuntimeError(f"Empty name for game at path : '{path}'")
        
        self.path = path
        self.name = name
        self.driver = driver
        
    def run_with_subscriber(self, mqtt_sub):
        self.driver(mqtt_sub)
        return Popen(self.path)