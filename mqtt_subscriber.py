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
import threading

def connect_to_device(on_message, on_disconnect)-> mqtt.Client | int:
    """
    Connect to device via mqtt

    on_message: callback receiving mqtt messages

    msg.payloads contains a value ranging from -10.0 to 10.0 under normal circumstances
    going up to -20.0 + 20.0 when spinned by hand.
    
    returns the mqtt client responsible for the connection or an MQTT Error Code is something went wrong.

    if no message is received for 1 second, on_disconnect will be called.
    """
    client = mqtt.Client()
    timer = threading.Timer(1.0, on_disconnect)
    timer.start()

    def on_message_wrapper(x, y, msg):
        nonlocal timer
        nonlocal on_message
        timer.cancel()
        timer = threading.Timer(1.0, on_disconnect)
        timer.start()
        on_message(msg)


    client.on_message=on_message_wrapper

    res = client.connect('10.42.0.1')

    if res != mqtt.MQTT_ERR_SUCCESS:
        return res

    res = client.subscribe("fit_and_fun/speed")

    if res[0] != mqtt.MQTT_ERR_SUCCESS:
        return res
    
    res = client.loop_start()
    
    if res != mqtt.MQTT_ERR_SUCCESS:
        return res

    return client