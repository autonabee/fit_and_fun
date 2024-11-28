#!/bin/sh
sudo apt install python3 python3-tk python3-pip
pip3 install -r ./requirements.txt
sudo apt install -y mosquitto  mosquitto-clients