# fit_and_fun

An interactive device to make a hand pedal fun

Première version avec un capteur MStick5C-P qui envoie la vitesse de rotation du capteur par MQTT/wifi à un jeu pygame
sur PC.

## Pre-requis

Sur le PC-ubuntu/Raspberry:

* python 3.10
* sudo apt install -y mosquitto  mosquitto-clients
* pip install -y pygame paho-mqtt

## Liens utiles

* M5stackC-Plus
  * https://docs.m5stack.com/en/core/m5stickc_plus
  * https://github.com/m5stack/M5StickC-Plus
  * https://community.m5stack.com/
  * https://www.hackster.io/m5stack/
* MQTT
  * https://randomnerdtutorials.com/esp32-mqtt-publish-subscribe-arduino-ide/
  * https://diyi0t.com/introduction-into-mqtt/
  * https://learn.sparkfun.com/tutorials/introduction-to-mqtt
  * https://medium.com/python-point/mqtt-basics-with-python-examples-7c758e605d4
  * https://www.tutos.eu/4910

## TODO


* [x] Tuto MQTT
* [x] echange MQTT ESP32-IMU/PC (arduino/Python)
* [x] jeu avec clavier en client MQTT
* [x] intégration soft IMU avec le jeu
* [ ] intégration raspberry
* [ ] Test écran
* [ ] IMU bosh + esp32
* [ ] Tuto ceinture cardio
