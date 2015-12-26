
from time import sleep
import re
import setup
import traceback
from setup import botlog, reader, SERIAL_BAUD_RATE

import authenticate
import door_hw


botlog.info( '%s Starting.' % setup.botname)
reader.initialize(baud_rate=setup.SERIAL_BAUD_RATE)

blinker = 0
while True :

    try :
        blinker += 1
        if blinker%10 == 0 :
            door_hw.green(False)
        sleep(.1)
        door_hw.green(True)

        # Get a card
        #
        rfid_str = reader.get_card()
        if not rfid_str :
            continue

        botlog.debug( 'RFID string >>%s<<' % rfid_str)

        # Several things can happen:
        # 1. some error in reading.
        # 2. good card, not allowed
        # 3. good card, allowed: yay!
        # 4. bad card from some reason
        # 5. unknown card
        try :
            rfid = int(rfid_str)

            access = authenticate.get_access(rfid)


            if access :
                (username,allowed) = access


                if 'allowed' in allowed :

                    #3, yay!
                    #
                    botlog.info('%s allowed' % username)

                    # open the door
                    # 
                    door_hw.open_sesame()

                else :
                    #2
                    # access failed.  blink the red
                    #
                    botlog.warning('%s DENIED' % username)
                    door_hw.blink_red()           

            else :
                #5
                botlog.warning('Unknown card %s ' % rfid_str)
                door_hw.blink_red()           

        except :
            #4
            # bad input catcher, also includes bad cards
            #
            botlog.warning('bad card %s ' % rfid_str)
            door_hw.blink_red(4)

    except :
        e = traceback.format_exc().splitlines()[-1]
        botlog.error('door loop unexpected exception: %s' % e)
        pass

    sleep(3)
    reader.flush()  # needed for serial reader that keeps sending stuff.
    


# 0001258648

