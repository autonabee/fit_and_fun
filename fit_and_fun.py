import argparse
#from console import Console
from game_canoe import GameCanoe
from mqtt_subscriber import mqtt_subscriber

# Main
if __name__ == "__main__":
    """Launch the game"""
    PARSER = argparse.ArgumentParser(
        description='Fit and fun game during sport') 
    PARSER.add_argument('-b', '--broker', dest='broker',
                        help='Broker host to connect (default localhost)', default='localhost')
    ARGS = PARSER.parse_args()
    console=GameCanoe()
    mqtt_sub=mqtt_subscriber(console.get_speed, console.synchro, 'fit_and_fun/speed', broker_addr=ARGS.broker)
    mqtt_sub.run()
    console.menu()
 