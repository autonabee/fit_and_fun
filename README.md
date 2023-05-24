# fit_and_fun

An interactive device to make a hand pedal fun

Première version avec un capteur MStick5C-P qui envoie la vitesse de rotation du capteur par MQTT/wifi à un jeu pygame
sur PC.

## Pre-requis

### Raspberry

#### Build & libs

* Raspberry Pi OS Full (64 bit) a port of debian bullseye with desktop (humanlab/humanlab)
* Execute `install.sh`

#### Mqtt broker config

Add at this end of the file: `/etc/mosquitto/mosquitto.conf`
```
listener 1883 localhost 
listener 1883 10.42.0.1
allow_anonymous true
```

Restart the service
```
systemctl restart mosquitto
```

Some reminders to debug

* see the log: `sudo tail -f /var/log/mosquitto/mosquitto.log`
* connection to the socket port: `nc -z -v -u 10.42.0.1 1883`
* connection to the topic through the broker:`mosquitto_sub -h 10.42.0.1 -t "fit_and_fun/speed"`
* publish a topic: `mosquitto_pub -h 10.42.0.1 -t "fit_and_fun/speed" -mode "10.0"`

#### Wifi access point

* Suivre : <https://www.tomshardware.com/how-to/raspberry-pi-access-point>
* Par configuration graphique: `ssid=fit_and_fun`
* Pas de sécurité
* S'assurer que le Raspberry se connecte automatiquement sur le réseau fit_and_fun, et que son adresse IP statique est 10.42.0.1

#### Réglages Ecran

* LCD 9 pouces, 1024x600, 43 euros : <https://fr.aliexpress.com/item/32954126627.html>
* manuel utilisateur: <https://usermanual.wiki/Pdf/ERVB800168Datasheet.1273732525/html>

* Ajout dans ```/boot/config.txt```
```
hdmi_group=2
hdmi_mode=87
hdmi_cvt=1024 600 60 6 0 0 0
hdmi_drive=1
```

* Modification de ```/boot/cmdline.txt```
```
[...] video=HDMI-A-1:1024x600M@60,margin_left=0,margin_right=0,margin_top=0,margin_bottom=0
```
__Attention__ : À ajouter sur la même ligne que les autres instructions
__Attention__ : Ajouter un espace entre le reste des instructions et celle-ci

#### Démarrage automatique du prog Python

* Modification de ```/etc/xdg/lxsession/LXDE-pi/autostart```, ajouter :
```
@lxterminal
```

* Ajouter dans le .bashrc :
```
DISPLAY=:0 xrandr --output HDMI-1 --rotate left
xinput set-prop 'WaveShare WS170120' 'Coordinate Transformation Matrix' 0 -1 1 1 0 0 0 0 1
systemctl start mosquitto
cd [your_path]/fit_and_fun
python fit_and_fun.py -f
```

### M5Stick-C P

* Capteur inertiel : M5stickC-Plus : <https://www.gotronic.fr/art-module-m5stickc-plus-k016-p-33740.htm>
* Config Arduino: <https://docs.m5stack.com/en/quick_start/m5stickc_plus/arduino> pour installation libs et plateforme.
* lib mqtt: <https://www.arduino.cc/reference/en/libraries/pubsubclient>
* Programmer (configurer access wifi et IP broker): `FAF_STICK5/FAF_STICK5.ino`

### ESP2866+BNO05

* micro-controleur ESP2866 avec une IMU BNO05 via I2C
* <https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor>
* lib mqtt: <lib https://www.arduino.cc/reference/en/libraries/pubsubclient>
* Programmer (configurer access wifi et IP broker): `FAF_ESP/FAF_ESP.ino`

## Démo qui tourne

### Sur Raspberry

__Attention__ : Avant de lancer le programme pour la première fois, exécuter :
```
python reset_database.py
```

Avec le raspberry en wifi access-point (ssid:fit_and_fun) et un écran classique sur la raspberry. Après configuration Wifi/Mqtt coté raspberry (`sudo systemctl restart mosquitto`) et mis sous tension le capteur ESP2866+BNO05, on peut lancer le jeu: `python fit_and_fun.py -f`.
Quand le capteur tourne sur lui-même (axe Z), la rivière avance et si on passe une certaine vitesse, le personnage avance aussi. Le score augmente en fonction de la durée/vitesse et si le personnage touche les obstacles  qui traverse la rivière.

### Sur une autre machine

__Attention__ : Avant de lancer le programme pour la première fois, exécuter :
```
python reset_database.py
```

Avec le raspberry allumé en wifi access-point (ssid:fit_and_fun), et un capteur (ESP+BN0 ou M5Stick) :
Connecter l'appareil au réseau Wi-Fi `fit_and_fun` et lancer le programme : `python fit_and_fun.py -b 10.42.0.1`

## Options d'exécution

* `-b [host_ip]` : Spécifie l'adresse du broker MQTT (localhost par défaut)
* `-d` : Active le mode debug qui affiche des infos supplémentaires dans la console
* `-f` : Affiche le jeu en mode plein écran ; déconseillé sur un appareil dont la résolution n'est pas 1024x600
* `-l` : Ne se connecte pas au broker MQTT

## Fichiers

* `console.py`: Entry menu of the game before launching the Canoe game
* `game_canoe.py`: Canoe game (GameCanoe inherit from Console)
* `game_entities.py`: pygame elements for Canoe game
* `fit_and_fun_keyboard.py`: main to launch the game with keyboard interaction (without mqtt)
* `mqtt_subscriber.py`: mqtt subscriber to read the topic `fit_and_fun/speed`
* `sensor_keyboard.py`: main to control the game in the other part with keyboard interaction (with mqtt)
* `fit_and_fun.py`: main to launch the game controllable through mqtt (topic `fit_and_fun/speed`)
* `reset_database.py` : python script which resets the database stored as `fit_and_fun.db`
* `sensors/FAF_ESP/FAF_ESP.ino`: firmware for the gyro sensor (ESP2866+BNO05) sending rot speed through mqtt
* `sensors/FAF_STICK5/FAF_STICK5.ino`: firmware for the gyro sensor (M5StickC-P), sending rot speed through mqtt to be tested.

## Problèmes non résolus

### Wifi Access point

La connexion Wi-Fi fonctionne si le hotspot partagé ne possède pas de sécurité (WEP, WPA2, etc.)
Aucune des deux cartes (M5Stick ou ESP32) ne parvient à se connecter si le hotspot est sécurisé. Il s'agit probablement d'un problème au niveau de la bibliothèque "WiFi.h" d'Arduino ou bien de la manière dont le réseau est partagé depuis le Raspberry. Pas d'info utile trouvée sur Internet ; à chercher...

## Liens utiles

* Pygame
 
  * <https://pythonfaqfr.readthedocs.io/en/latest/pygame_collisions.html>

* M5stackC-Plus
  * <https://docs.m5stack.com/en/core/m5stickc_plus>
  * <https://github.com/m5stack/M5StickC-Plus>
  * <https://community.m5stack.com>
  * <https://www.hackster.io/m5stack>
* MQTT
  * <https://randomnerdtutorials.com/esp32-mqtt-publish-subscribe-arduino-ide>
  * <https://diyi0t.com/introduction-into-mqtt>
  * <https://learn.sparkfun.com/tutorials/introduction-to-mqtt>
  * <https://medium.com/python-point/mqtt-basics-with-python-examples-7c758e605d4>
  * <https://www.tutos.eu/4910>
* Config Ecran
  * <https://www.raspberrypi.com/documentation/computers/config_txt.html>
* Wifi access point
  * <https://www.tomshardware.com/how-to/raspberry-pi-access-point>

## TODO
