# This file is a part of Fit & Fun
#
# Copyright (C) 2023 Inria/Autonabee
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

import paho.mqtt.client as mqtt
import readchar 

VEL_MIN=0.0
VEL_MAX=30.0
VEL_INC=5.0

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
        velocity+=VEL_INC
        if velocity > VEL_MAX:
            velocity = VEL_MAX

    elif key == 'z':
        velocity-=VEL_INC
        if velocity < VEL_MIN:
            velocity = VEL_MIN

    elif key == 'e':
        velocity=0.0

    elif key == 'q':
        run = False
    print('Velocity:',velocity)
    client.publish("fit_and_fun/speed", str(velocity))
    
print('Bye...')