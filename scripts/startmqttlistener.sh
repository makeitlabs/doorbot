#!/bin/sh

cd /home/pi/doorbot/databases
su pi -c "python3 mqtt_acl.py > /dev/null < /dev/null" & 
