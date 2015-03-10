

from time import sleep
import re


import authenticate
import door_hw


while True :

    # Get a line
    #
    rfid_str = raw_input('input rfid? ')

    print '>>%s<<' % rfid_str,

    ##m = re.match('k:(\d+)',response)
   ## if m:
        ##rfid = int(m.groups()[0])

    try :
        rfid = int(rfid_str)

        access = authenticate.get_access(rfid)

        if access :
            (username,allowed) = access

            if int(allowed) == 0 :
                raise  Exception

            print 'Welcome, %s!' % username

            # open the door
            # 
            door_hw.open_sesame()

        else :
            # access failed.  blink the red
            #
            print 'ACCESS DENIED'
            door_hw.blink_red()           

    except :
        # bad input catcher, also includes bad cards
        #
        print 'Bad input'
        door_hw.blink_red(4)


# 0001258648
