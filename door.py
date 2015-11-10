
from time import sleep
import re
import setup
from setup import botlog

import authenticate
import door_hw


botlog.info( '%s Starting.' % setup.botname)

while True :

    # Get a line
    #
    rfid_str = raw_input('input rfid? ')

    botlog.debug( '>>%s<<' % rfid_str)

    try :
        rfid = int(rfid_str)

        access = authenticate.get_access(rfid)

        if access :
            (username,allowed) = access

            if int(allowed) == 0 :
                raise  Exception

            botlog.info('%s allowed' % username)

            # open the door
            # 
            door_hw.open_sesame()

        else :
            # access failed.  blink the red
            #
            botlog.warning('%s DENIED' % username)
            door_hw.blink_red()           

    except :
        # bad input catcher, also includes bad cards
        #
        botlog.warning('bad card %s ' % rfid_str)
        door_hw.blink_red(4)


# 0001258648

