#!/bin/sh

cd /home/pi/doorbot
su pi -c "python3 qdoor.py > /dev/null < /dev/null" & 
