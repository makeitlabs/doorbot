

import logging
from rfid import *


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




# define the rfid reader device type
#
reader = rfid_reader_serial()
SERIAL_BAUD_RATE = 9600


# authenticate.py
#
card_data_file = 'databases/rfid/acl.json'



# door_hw.py
#

# no red LED so double up the green one
#
RED_PIN = 12
GREEN_PIN = 12
DOOR_PIN = 21
BEEP_PIN = None
