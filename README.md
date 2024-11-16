# fit_and_fun

An interactive device to make a hand pedal fun

# Contributors
Coders : Roger, Simeon, Clémentine, Rémi, Astrale, Cécile
NGOs : AutonaBee, MyHumanKit, Humanlab Saint-Pierre

# Material
## Harware
- Raspberry (tested version : 4 Model B - OS Rasbian)
- ESP 32
- LCD 9 pouces, 1024x600, 43 euros : <https://fr.aliexpress.com/item/32954126627.html>
(User manual : <https://usermanual.wiki/Pdf/ERVB800168Datasheet.1273732525/html>)

## CAD file
To be uploaded

## Homemade Electronic
To be uploaded

# Start the program
## Options d'exécution

* `-b [host_ip]` : Spécifie l'adresse du broker MQTT (localhost par défaut)
* `-d` : Active le mode debug qui affiche des infos supplémentaires dans la console
* `-f` : Affiche le jeu en mode plein écran ; déconseillé sur un appareil dont la résolution n'est pas 1024x600
* `-l` : Ne se connecte pas au broker MQTT
* `-o [portrait|landscape]` : Lance le jeu en portrait ou en paysage (portrait par défaut)
  
## On the AutonaBee's setup - WORKING DEMO
To be documented


## On Raspberry 
__Attention__ : Avant de lancer le programme pour la première fois, exécuter :
```
python reset_database.py
```

Avec le raspberry en wifi access-point (ssid:fit_and_fun) et un écran classique sur la raspberry. Après configuration Wifi/Mqtt coté raspberry (`sudo systemctl restart mosquitto`) et mis sous tension le capteur ESP2866+BNO05, on peut lancer le jeu: `python fit_and_fun.py -f`.
Quand le capteur tourne sur lui-même (axe Z), la rivière avance et si on passe une certaine vitesse, le personnage avance aussi. Le score augmente en fonction de la durée/vitesse et si le personnage touche les obstacles  qui traverse la rivière.

## On another system
__Attention__ : Avant de lancer le programme pour la première fois, exécuter :
```
python reset_database.py
```

Avec le raspberry allumé en wifi access-point (ssid:fit_and_fun), et un capteur (ESP+BN0 ou M5Stick) :
Connecter l'appareil au réseau Wi-Fi `fit_and_fun` et lancer le programme : `python fit_and_fun.py -b 10.42.0.1`

# Files description

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

# First Installation

## Install first librairies
- Python 3.9 - Main code
- Mosquitto (sudo apt install -y mosquitto  mosquitto-clients) - Libraity to interface MQTT broker
- Pygame (pip install -y pygame pygame-menu paho-mqtt readchar) - Librairy for the game graphic design and dynamics

## Configure the MQTT broker
Add at this end of the file: `/etc/mosquitto/mosquitto.conf`
```
listener 1883 localhost 
listener 1883 10.42.0.1
allow_anonymous true
```

- Restart the service
```
systemctl restart mosquitto
```
Some tips to debug
* see the log: `sudo tail -f /var/log/mosquitto/mosquitto.log`
* connection to the socket port: `nc -z -v -u 10.42.0.1 1883`
* connection to the topic through the broker:`mosquitto_sub -h 10.42.0.1 -t "fit_and_fun/speed"`
* publish a topic: `mosquitto_pub -h 10.42.0.1 -t "fit_and_fun/speed" -mode "10.0"`

## Configure Wifi access point

* Follow instruction from : <https://www.tomshardware.com/how-to/raspberry-pi-access-point>
* At the step "Setting up the Access Point on Raspberry Pi", give the name to the network : `fit_and_fun` and  select the mode "No security"
* Check automatic connection of the Raspberry to network "fit_and_fun", and that the static IP is 10.42.0.1

## Configure screen parameters
* Add in ```/boot/config.txt```
```
hdmi_group=2
hdmi_mode=87
hdmi_cvt=1024 600 60 6 0 0 0
hdmi_drive=1
```

* Modify file  ```/boot/cmdline.txt```
```
[...] video=HDMI-A-1:1024x600M@60,margin_left=0,margin_right=0,margin_top=0,margin_bottom=0
```
__Attention__ : add on the same line as the other instructions
__Attention__ : add a space in between

## Start Python main program for the first time - TO BE TESTED
* Modification de ```/etc/xdg/lxsession/LXDE-pi/autostart```, ajouter :
```
@lxterminal
```

* Connaître l'identifiant de l'écran, exécuter la commande
```xinput```
et copier le résultat qui correspond à l'appareil utilisé. Par exemple, avec l'écran WaveShare conseillé, l'identifiant correspondant est `WaveShare WS170120`

* Ajouter dans le .bashrc :
```
DISPLAY=:0 xrandr --output HDMI-1 --rotate left
xinput set-prop '[screen_id]' 'Coordinate Transformation Matrix' 0 -1 1 1 0 0 0 0 1
systemctl start mosquitto
cd [your_path]/fit_and_fun
python fit_and_fun.py -f
```
## Configure the Hardware
TO BE UPDATED FROM ARCHIVE

# Problems to solve

- Wifi Access point
La connexion Wi-Fi fonctionne si le hotspot partagé ne possède pas de sécurité (WEP, WPA2, etc.)
Aucune des deux cartes (M5Stick ou ESP32) ne parvient à se connecter si le hotspot est sécurisé. Il s'agit probablement d'un problème au niveau de la bibliothèque "WiFi.h" d'Arduino ou bien de la manière dont le réseau est partagé depuis le Raspberry. Pas d'info utile trouvée sur Internet ; à chercher...



# Liens utiles

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

# Licenses

* Le logiciel est sous licence [Cecill](./COPYING)
* Les boitiers sont sous licence [Creative-Common](cad/COPYING.md)



----------------------------------------------------------------------------------------
# Archive
Première version avec un capteur MStick5C-P qui envoie la vitesse de rotation du capteur par MQTT/wifi à un jeu pygame
sur PC.

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






## Pour ajouter un jeu

Pour ajouter un nouveau, il faut respecter 3 points

### Créer la classe contenant le code du jeu

Créer une classe (dans un fichier à part) contenant au moins un contructeur sous cette forme :
```
def __init__(self, console, stages):
        self.console = console
        self.screen = console.screen
```
et une fonction `game()` contenant la définition du jeu

Le fichier `game_data.py` contient un exemple simple d'une telle classe.

### Ajouter le nouveau jeu dans la BDD

Dans un terminal :
```
sqlite3 fit_and_fun.db
```
puis
```
INSERT INTO Game (id, display_name, class_name) VALUES ((SELECT max(id) FROM Game) + 1, '[display_name]', '[class_name]');
```
avec `display_name` le nom du jeu tel qu'il doit apparaître dans l'interface, et `class_name` le nom de la classe créée dans l'étape précédente.

### Modifier console.py
Dans `console.py`, modifier le corps de la fonction `launch_selected_game`, ajouter :
```
elif self.current_game[1] == '[class_name]':
            game = [class_name](self, stages)
```
avec `class_name` le nom de la classe créée précédemment.

