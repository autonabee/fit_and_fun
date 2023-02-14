import paho.mqtt.client as mqtt
import threading

class mqtt_subscriber():
    """ Mqtt subscriber to receive a raw rotational speed"""
    def __init__(self, on_message, synchro, topics, broker_addr='localhost'):
        """
        Class constructor

        Parameter:
        ---------
        on_message: callback function
            mqtt callback subscriber to get the value

        synchro: threading.Lock
            to synchronize the end of the client subscriber
        
        broker_addr: string
            broker address (name or IP) in action

        topics: [string]
            Mqtt topics to be subscribed
        
        """
        self.on_message=on_message
        self.mqttBroker = broker_addr
        self.topics = topics
        # Lock thread synchronization
        self.lock = synchro
        self.lock.acquire()
        self.debug=True


    def subscribe_connect(self):
        """ client function launched in a thread
        """
        if self.debug==True: print("Start mqtt subscriber")
        # Broker connection
        client = mqtt.Client("Console")
        client.connect(self.mqttBroker) 
        # Topics 'fit_and_fun/speed' subscription
        client.loop_start()
        for topic in self.topics:
            client.subscribe(topic)
        client.on_message=self.on_message 
        # Wait for the end
        self.lock.acquire()
        client.loop_stop()
        if self.debug==True: print("End mqtt subscriber")
   
    def run(self):
        """ Start the thread """
        self.t1=threading.Thread(target=self.subscribe_connect)
        self.t1.start()

    def stop(self):
        """ Stop the thread """
        self.lock.release()
        self.t1.join()

if __name__ == "__main__":
    """ Exemple of subscriber use"""

    lock = threading.Lock()
    
    def get_msg(self, client, userdata, message):
        try:
            rot_speed=float(str(message.payload.decode("utf-8"))) 
        except Exception:
            print('Error in mqtt message')
            self.speed=0
            self.rot_speed=0

    mqtt_sub=mqtt_subscriber(get_msg, lock, 'fit_and_fun/speed')
    lock.acquire()