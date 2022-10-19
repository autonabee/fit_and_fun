from console import Console
from mqtt_subscriber import mqtt_subscriber

# Main
if __name__ == "__main__":
    console=Console()
    mqtt_sub=mqtt_subscriber(console.get_speed, console.synchro, 'fit_and_fun/speed')
    mqtt_sub.run()
    console.game()
