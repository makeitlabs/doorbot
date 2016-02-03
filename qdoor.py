from PyQt4.QtCore import QThread, QCoreApplication, QTimer, QSocketNotifier

import signal
import sys
from time import sleep
import re
import qsetup
import traceback
from qsetup import botlog

import qauthenticate
from qdoor_hw import DoorHW
from qrfid import rfid_reader

def sigint_handler(*args):
    QCoreApplication.quit()
        

class RFIDReaderThread(QThread):
    
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False

        self.hw = DoorHW(red_pin=qsetup.RED_PIN, green_pin=qsetup.GREEN_PIN, door_pin=qsetup.DOOR_PIN, beep_pin=qsetup.BEEP_PIN)

        self.reader = rfid_reader.factory(qsetup.READER_TYPE)
        self.reader.initialize(baud_rate=qsetup.READER_BAUD_RATE)
        
        botlog.info( '%s Thread Initialized.' % qsetup.botname)
        
    def __del__(self):
        botlog.info( '%s Thread Deletion.' % qsetup.botname)
        self.exiting = True
        self.wait()

    def blink(self):
        print('blink phase %s' % self.blinkPhase)
        self.hw.green(on=self.blinkPhase)
        self.blinkPhase = not self.blinkPhase

    def latch(self):
        self.hw.latch(open=False)
        self.hw.green(on=False)

    def onData(self):
        rfid_str = self.reader.get_card()
        if not rfid_str:
            return
        
        botlog.debug( 'RFID string >>%s<<' % rfid_str)

        # Several things can happen:
        # 1. some error in reading.
        # 2. good card, not allowed
        # 3. good card, allowed: yay!
        # 4. bad card from some reason
        # 5. unknown card
        try :
            rfid = int(rfid_str)
            
            access = qauthenticate.get_access(rfid)
                    
            if access:
                (username,allowed) = access

                if 'allowed' in allowed :
                    #3, yay!
                    #
                    botlog.info('%s allowed' % username)

                    # open the door
                    #
                    #self.hw.open_sesame()
                    self.hw.latch(open=True)
                    self.hw.green(on=True)
                    self.latchTimer.setSingleShot(True)
                    self.latchTimer.start(4000)

                else :
                    #2
                    # access failed.  blink the red
                    #
                    botlog.warning('%s DENIED' % username)
                    #self.hw.blink_red()           

            else :
                #5
                botlog.warning('Unknown card %s ' % rfid_str)
                #self.hw.blink_red()           

        except :
            #4
            # bad input catcher, also includes bad cards
            #
            botlog.warning('bad card %s ' % rfid_str)
            # other exception?
            e = traceback.format_exc().splitlines()[-1]
            botlog.error('door loop unexpected exception: %s' % e)
            #self.hw.blink_red(4)

        #sleep(3)
        #self.reader.flush()  # needed for serial reader that keeps sending stuff.
        
    def run(self):
        botlog.info( '%s Thread Running.' % qsetup.botname)

        self.blinkPhase = False
        self.blinkTimer = QTimer()
        self.blinkTimer.timeout.connect(self.blink)        

        self.latchTimer = QTimer()
        self.latchTimer.timeout.connect(self.latch)
        
        self.notifier = QSocketNotifier(self.reader.fileno(), QSocketNotifier.Read)
        self.notifier.activated.connect(self.onData)
        
        self.blinkTimer.start(250)
        self.notifier.setEnabled(True)

        self.exec()
        
        botlog.info( '%s Thread Stopped.' % qsetup.botname)



if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    
    app = QCoreApplication(sys.argv)
    rfid = RFIDReaderThread()

    rfid.start()
    app.exec()
