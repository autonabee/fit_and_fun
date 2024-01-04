#!/bin/sh
DISPLAY=:0 xrandr --output HDMI-1 --rotate left
xinput set-prop 'WaveShare WS170120' 'Coordinate Transformation Matrix' 0 -1 1 1 0 0 0 0 1