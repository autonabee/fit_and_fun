import pathlib
from subprocess import Popen


class Game(object):
    """
    A game compatible with the fit_and_fun hardware.

    exec_name : the name of the game

    exec_path : path to the game

    driver    : A function that accepts a MQTT message and converts it to inputs for the game, most likely using uinput or pynput.
    """

    def __init__(self, name: str, path: str, driver):
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



rot = 0
first = True
is_pressed = False

def print_game_driver(msg):
    """
    The rot value is going to be updated frequently, we check it every 0.05 second 
    and if the state of turning the wheel has changed, we enter or release a touch.
    """
    global first
    global rot
    print("print game driver with: ", msg.payload.decode("utf",  errors="ignore"))
    # time.sleep(2)
    timer = threading.Timer(1000000000, lambda: None)
    # todo launch onceqqq
    def target():
        global rot
        global is_pressed
        print("target print game activated")
        while True:
            time.sleep(0.05)            
            if rot == 0.0 and not is_pressed:
                # print("not pressed no change")
                continue
            elif rot != 0.0 and is_pressed:
                # print("pressed no change")
                continue
            elif rot == 0:
                print("release")
                is_pressed = False
                pgui.keyUp("a")
            else:
                print("press")
                pgui.keyDown("a")
                is_pressed = True
    if first:
        threading.Thread(target=target).start()
        first = False
    rot = float(msg.payload.decode('utf8', errors="ignore"))


PrintGame = Game("print game", "games/print_game_launcher.py", print_game_driver)
