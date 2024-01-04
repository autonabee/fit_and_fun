#!/bin/sh
DISPLAY=:0 xrandr --output HDMI-1 --rotate normal
xinput set-prop 'WaveShare WS170120' 'Coordinate Transformation Matrix' 1 0 0 0 1 0 0 0 1