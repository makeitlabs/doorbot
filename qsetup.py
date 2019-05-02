import logging
from logging.handlers import SysLogHandler
from qrfid import *
from qschedule import Schedule

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
READER_DEVICE = '/dev/ttyS0'
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
schedule = Schedule.factory('entry')

# door_hw.py
#
#
RED_PIN = 16
GREEN_PIN = 13
DOOR_PIN = 4
BEEP_PIN = 26

