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
    ARGS = PARSER.parse_args()

    wind_resistor=None
    if ARGS.wind==True:
        wind_resistor=wind()
        wind_resistor.run()
    console=GameCanoe(wind=wind_resistor) 
    #console=GameCanoe()
    mqtt_sub=mqtt_subscriber(console.get_speed, console.synchro, 'fit_and_fun/speed', 
                            broker_addr=ARGS.broker)
    mqtt_sub.run()
    console.menu()
 