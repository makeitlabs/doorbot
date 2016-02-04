from PyQt4.QtCore import QThread, QCoreApplication, QTimer, QSocketNotifier

from enum import Enum
import signal
import sys
from time import sleep
import re
import qsetup
import traceback
from qsetup import botlog

from qauthenticate import *
from qdoor_hw import DoorHW
from qrfid import rfid_reader

def sigint_handler(*args):
    QCoreApplication.quit()
        

class Status(Enum):
    INIT = 'init'
    READY = 'ready'
    READING = 'reading'
    DENIED = 'denied'
    ALLOWED = 'allowed'
    UNKNOWN = 'unknown'
    LATCHED = 'latched'
    ERROR = 'error'
    
class RFIDReaderThread(QThread):
    
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.exiting = False

        self.status = Status.INIT
        
        self.hw = DoorHW(red_pin=qsetup.RED_PIN, green_pin=qsetup.GREEN_PIN, door_pin=qsetup.DOOR_PIN, beep_pin=qsetup.BEEP_PIN)

        self.reader = rfid_reader.factory(qsetup.READER_TYPE)
        self.reader.initialize(baud_rate=qsetup.READER_BAUD_RATE)

        self.authenticate = Authenticate.factory(qsetup.AUTHENTICATE_TYPE, qsetup.AUTHENTICATE_FILE)
        
        botlog.info( '%s Thread Initialized.' % qsetup.botname)
        
    def __del__(self):
        botlog.info( '%s Thread Deletion.' % qsetup.botname)
        self.exiting = True
        self.wait()

    def updateLEDs(self):
        if self.status == Status.INIT:
            self.hw.green(on=True)
            self.hw.red(on=True)
        elif self.status == Status.READY:
            self.hw.green(on=self.blinkPhase)
            self.hw.red(on=False)
        elif self.status == Status.DENIED or self.status == Status.UNKNOWN:
            self.hw.green(on=False)
            self.hw.red(on=True)
        elif self.status == Status.ALLOWED or self.status == Status.LATCHED:
            self.hw.green(on=True)
            self.hw.red(on=False)
        elif self.status == Status.ERROR:
            self.hw.green(on=False)
            self.hw.red(on=self.blinkPhase)
        
    def blink(self):
        self.updateLEDs()
        self.blinkPhase = not self.blinkPhase

    def setStatus(self, s):
        botlog.debug('status change from %s to %s' % (self.status, s))
        self.status = s
        self.updateLEDs()
        
    def unlatch(self):
        self.hw.latch(open=False)
        self.setStatus(Status.READY)
        self.reader.flush()
        self.notifier.setEnabled(True)

    def undelay(self):
        self.setStatus(Status.READY)
        self.reader.flush()
        self.notifier.setEnabled(True)

        
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
            self.setStatus(Status.READING)
            rfid = int(rfid_str)
            
            access = self.authenticate.get_access(rfid)
                    
            if access:
                allowed = access['allowed']
                member = access['member']

                if 'allowed' in allowed :
                    #3, yay!
                    #
                    botlog.info('%s allowed' % member)

                    # open the door
                    #
                    #self.hw.open_sesame()
                    self.setStatus(Status.ALLOWED)
                    self.setStatus(Status.LATCHED)

                    self.hw.latch(open=True)
                    self.notifier.setEnabled(False)
                    self.latchTimer.start(4000)

                else :
                    #2
                    # access failed.  blink the red
                    #
                    botlog.warning('%s DENIED' % member)
                    self.setStatus(Status.DENIED)
                    self.notifier.setEnabled(False)
                    self.delayTimer.start(3000)


            else :
                #5
                botlog.warning('Unknown card %s ' % rfid_str)
                self.setStatus(Status.UNKNOWN)
                self.notifier.setEnabled(False)
                self.delayTimer.start(3000)
                

        except :
            #4
            # bad input catcher, also includes bad cards
            #
            botlog.warning('bad card %s ' % rfid_str)
            # other exception?
            e = traceback.format_exc().splitlines()[-1]
            botlog.error('door loop unexpected exception: %s' % e)
            self.setStatus(Status.ERROR)
            self.notifier.setEnabled(False)
            self.delayTimer.start(3000)

            
        
    def run(self):
        botlog.info( '%s Thread Running.' % qsetup.botname)

        self.blinkPhase = False
        self.blinkTimer = QTimer()
        self.blinkTimer.timeout.connect(self.blink)        

        self.latchTimer = QTimer()
        self.latchTimer.timeout.connect(self.unlatch)
        self.latchTimer.setSingleShot(True)

        self.delayTimer = QTimer()
        self.delayTimer.timeout.connect(self.undelay)
        self.delayTimer.setSingleShot(True)
        
        self.notifier = QSocketNotifier(self.reader.fileno(), QSocketNotifier.Read)
        self.notifier.activated.connect(self.onData)
        
        self.blinkTimer.start(250)
        self.notifier.setEnabled(True)

        self.setStatus(Status.READY)
        self.exec()
        
        botlog.info( '%s Thread Stopped.' % qsetup.botname)



if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    
    app = QCoreApplication(sys.argv)
    rfid = RFIDReaderThread()

    rfid.start()
    app.exec()
