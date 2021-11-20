import logging
from logging.handlers import SysLogHandler
from qrfid import *
from qschedule import Schedule
import fcntl
import socket
import struct

botname = 'doorbot'


# global app logging
#

botlog = logging.getLogger(botname)
hdlr = logging.FileHandler('%s.log' % botname)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
# the file log gets all but debug info
hdlr.setLevel(logging.INFO)
botlog.addHandler(hdlr) 


# define a Handler which writes all messages  to the sys.stderr
#
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
# root logger should handle everything
#
botlog.setLevel(logging.DEBUG)

# remote syslog
syslog = SysLogHandler(address=('10.0.0.1', 514))
formatter = logging.Formatter('%(asctime)s : %(message)s', datefmt='%b %d %H:%M:%S')
syslog.setFormatter(formatter)
botlog.addHandler(syslog)




# define the rfid reader device type
#
#READER_TYPE = 'hid'

READER_TYPE = 'serial'
READER_DEVICE = '/dev/serial0'
READER_BAUD_RATE = 9600

#READER_TYPE = 'tormach'
#READER_DEVICE = '/dev/ttyACM0'


# authenticate.py
#
AUTHENTICATE_TYPE = 'json'
AUTHENTICATE_CSV_FILE = 'databases/rfid/CardData.csv'
AUTHENTICATE_JSON_FILE = 'databases/rfid/acl.json'
AUTHENTICATE_FILE = AUTHENTICATE_JSON_FILE

# qschedule.py
# specify 'Open' for 24/7 access or 'HobbyistRestricted' for hobbyists on weekend/nights only
schedule = Schedule.factory('Open')

# door_hw.py
#
#
RED_PIN = 16
GREEN_PIN = 13
DOOR_PIN = 4
BEEP_PIN = 26

# mqtt
#
#
def getMacAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', bytes(ifname, 'utf-8')[:15]))
    return ''.join('%02x' % b for b in info[18:24])
            

mqtt_broker_address='auth'
mqtt_broker_port=1883
mqtt_ssl_ca_cert='/home/pi/ssl/ca.crt'
mqtt_ssl_client_cert='/home/pi/ssl/client.crt'
mqtt_ssl_client_key='/home/pi/ssl/client.key'
mqtt_node_id=getMacAddr('eth0')
mqtt_prefix='ratt/status/node/' + mqtt_node_id
mqtt_listen_topic='ratt/control/broadcast/#'
mqtt_acl_update_topic='ratt/control/broadcast/acl/update'

# ACL update
acl_update_script='/home/pi/doorbot/databases/auto_door_list.sh'
