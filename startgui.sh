#!/bin/sh
export DISPLAY=:0
cd /home/pi/doorbot/gui
su pi -c "python3 guiclient.py > /dev/null < /dev/null" &

