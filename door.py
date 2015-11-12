
from time import sleep
import re
import setup
from setup import botlog, reader

import authenticate
import door_hw


botlog.info( '%s Starting.' % setup.botname)
reader.initialize()


while True :

    sleep(.1)

    # Get a card
    #
    rfid_str = reader.get_card()
    if not rfid_str :
        continue

    botlog.debug( '>>%s<<' % rfid_str)

    try :
        rfid = int(rfid_str)

        access = authenticate.get_access(rfid)


        if access :
            (username,allowed) = access


            if 'allowed' not in allowed :
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

    sleep(3)
    reader.flush()  # needed for serial reader that keeps sending stuff.
    


# 0001258648

