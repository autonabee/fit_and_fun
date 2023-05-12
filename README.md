# fit_and_fun

An interactive device to make a hand pedal fun

Première version avec un capteur MStick5C-P qui envoie la vitesse de rotation du capteur par MQTT/wifi à un jeu pygame
sur PC.

## Pre-requis

### Raspberry

#### Build & libs

* Raspberry Pi OS Full (64 bit) a port of debian bullseye with desktop (humanlab/humanlab)
* python > 3.9
* sudo apt install -y mosquitto  mosquitto-clients
* pip install -y pygame pygame-menu paho-mqtt readchar

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

* J'ai suivi : <https://www.tomshardware.com/how-to/raspberry-pi-access-point>
* par configuration graphique: `ssid=fit_and_fun, pwd=fun_and_fit, WPA/WPA2`

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
python3 fit_and_fun.py -f
```

* S'assurer que le Raspberry se connecte automatiquement sur le réseau fit_and_fun, et que son adresse IP statique est 10.42.0.1

### M5Stick-C P

* Capteur inertiel : M5stickC-Plus : <https://www.gotronic.fr/art-module-m5stickc-plus-k016-p-33740.htm>
* Config Arduino: <https://docs.m5stack.com/en/quick_start/m5stickc_plus/arduino> pour installation libs et plateforme.
* lib mqtt: <https://www.arduino.cc/reference/en/libraries/pubsubclient>
* Programmer (configurer access wifi et IP broker): `FAF_STICK5/FAF_STICK5.ino`

### ESP2866+BNO05

* micro-controleur ESP2866 avec une IMU BNO05 via I2C
* <https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor>
* lib mqtt: <lib https://www.arduino.cc/reference/en/libraries/pubsubclient>
## Démo qui tourne

Avec le raspberry en wifi access-point (ssid:fit_and_fun, passwd:fun_and_fit) et un écran classique sur la raspberry. Après configuration Wifi/Mqtt coté raspberry (`sudo systemctl restart mosquitto`) et mis sous tension le capteur ESP2866+BNO05, on peut lancer le jeu: `python fit_and_fun.py -b 10.42.0.1`.
Quand le capteur tourne sur lui-même (axe Z), la rivière avance et si on passe une certaine vitesse, le personnage avance aussi. Le score augmente en fonction de la durée/vitesse et si le personnage touche les obstacles  qui traverse la rivière.

On peut utiliser également le jeu avec un clavier: `python fit_and_fun_keyboard.py`

## Fichiers

* `console.py`: Entry menu of the game before launching the Canoe game
* `game_canoe.py`: Canoe game (GameCanoe inherit from Console)
* `game_entities.py`: pygame elements for Canoe game
* `fit_and_fun_keyboard.py`: main to launch the game with keyboard interaction (without mqtt)
* `mqtt_subscriber.py`: mqtt subscriber to read the topic `fit_and_fun/speed`
* `sensor_keyboard.py`: main to control the game in the other part with keyboard interaction (with mqtt)
* `fit_and_fun.py`: main to launch the game controllable through mqtt (topic `fit_and_fun/speed`)
* `sensors/FAF_ESP/FAF_ESP.ino`: firmware for the gyro sensor (ESP2866+BNO05) sending rot speed through mqtt
* `sensors/FAF_STICK5/FAF_STICK5.ino`: firmware for the gyro sensor (M5StickC-P), sending rot speed through mqtt to be tested.

## Problèmes non résolus

### Wifi Access point

NON BLOQUANT pour avancer, on peut se connecter au broker de la raspberry en passant par le wifi de la box. On pourrait même utiliser un broker internet.

L'idéal est tout de même de réaliser la connection entre le capteur et la raspberry à travers un access point depuis la raspberry. Mais pour l'instant le capteur n'arrive pas à se connecter au point d'access, il retourne 'SSID_NOT_VALID'.

* Le capteur retourne comme erreur: 'SSID_NOT_VALID'. ./sandbox/WIFI/WIFI.ino
* Il est pourtant reconnu dans la liste des SSID quand le capteur fait un scan. https://github.com/m5stack/M5StickC-Plus/blob/master/examples/Advanced/WIFI/WiFiScan/WiFiScan.ino

Pourtant d'autres machines (PC, tél) arrivent à se connecter à cet access-point. Il y a un bug pour le nom SSID dans la lib, où il faut éviter de mettre des blancs dans le nom (mais ici ce n'est pas le cas)

* Pas de piste réelle, à essayer en reprogrammant le capteur ESP8286 de Cécile ou un ESP32 ?

### Configuration Ecran

* https://forums.raspberrypi.com/viewtopic.php?t=14914

Après modification de la config, l'écran est mal affiché quand on passe sous 'X'. Au départ la bannière est bien affiché. C'est donc un problème de réglage sans doute un peu plus profond du gestionnaire d'affichage. J'ai essayé un peu de jouer avec les paramètres `hdmi_group, hdmi_mode...` sans grand succés. L'écran s'affiche un peu à la canalplus... Pb de frequence, entrelacement ? Difficile de trouver la doc de cet écran aliexpress :-(

* j'ai testé une version ubuntu 22.0 (affichage en wayland) => même combat
* l'écran fonctionne car quand je le mets en 2eme écran sur mon PC il est correctement configuré.
* peut-être pas s'emmerder et voir si il n'y a pas un écran 7 ou 10 pouces à Rennes de dispo ?

J'ai retrouvé de la doc. sur le controleur de l'écran:

* manuel utilisateur: https://usermanual.wiki/Pdf/ERVB800168Datasheet.1273732525/html
* https://www.openhacks.com/page/productos/id/1880/title/HDMI-4-Pi%3A-7#lightbox['galeria']/0/
* https://learn.adafruit.com/hdmi-uberguide/2396-7-touch-display-1024x600-mini-driver

Le dernier lien propose un `config.txt` pour ce contrôleur. Il me semble avoir essayé ces paramètres...mais on se sait jamais...

## Fichiers


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

* [ ] Tuto ceinture cardio
