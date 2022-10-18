import paho.mqtt.client as mqtt
import readchar 

VEL_MIN=0.0
VEL_MAX=700.0
VEL_INC=100.0

mqttBroker ='localhost'
client = mqtt.Client("Sensor-keyboard")
client.connect(mqttBroker) 

client.subscribe("fit_and_fun/speed")
client.publish("fit_and_fun/speed", "300")

velocity=0.0
run=True

print('Sensor keyboard fit_and_fun')
print('a (speed up) / z (speed up) / e (speed zero) / q (quit)')
while run: 
    key = readchar.readkey()
    if key == 'a':
        velocity+=100.0
        if velocity > VEL_MAX:
            velocity = VEL_MAX

    elif key == 'z':
        velocity-=100.0
        if velocity < VEL_MIN:
            velocity = VEL_MIN

    elif key == 'e':
        velocity=0.0

    elif key == 'q':
        run = False
    print('Velocity:',velocity)
    client.publish("fit_and_fun/speed", str(velocity))
    
print('Bye...')