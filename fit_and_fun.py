import argparse
#from console import Console
from game_canoe import GameCanoe
from mqtt_subscriber import mqtt_subscriber
from wind import wind

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
    PARSER.add_argument('-t', '--timer', dest='timer',
                        help='Define the duration of a game session (in seconds)', default='120')
    PARSER.add_argument('-c', '--controls', dest='controls', action='store_true',
                        help='Activates button controling')
    ARGS = PARSER.parse_args()

    wind_resistor=None
    if ARGS.wind==True:
        wind_resistor=wind()
        wind_resistor.run()
    #console=GameCanoe(wind=wind_resistor) 
    console=GameCanoe(ARGS.debug, ARGS.fullscreen, int(ARGS.timer))
    subscribes = ['fit_and_fun/speed']
    if ARGS.controls:
        subscribes += ['fit_and_fun/select','fit_and_fun/down']
    mqtt_sub=mqtt_subscriber(console.message_callback, console.synchro, subscribes, 
                            broker_addr=ARGS.broker)
    mqtt_sub.run()
    console.display_select_user_ui()
 