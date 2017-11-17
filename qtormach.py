from PyQt4.QtCore import QThread, QCoreApplication, QTimer, QSocketNotifier, pyqtSignal, pyqtSlot
from PyQt4.QtNetwork import QLocalServer

from enum import Enum, unique
import signal
import sys
from time import sleep
import re
import traceback
from datetime import datetime, date, time
import qsetup
from qsetup import botlog
from qauthenticate import *
from qrfid import rfid_reader

def sigint_handler(*args):
    QCoreApplication.quit()
        
@unique
class Status(Enum):
    INIT = 0
    READY = 1
    READING = 2
    DENIED = 3
    ALLOWED = 4
    UNKNOWN = 5
    ERROR = 6

class SocketServerThread(QThread):
    def __init__(self, parent=None, readerThread=None):
        QThread.__init__(self, parent)

        self.readerThread = readerThread;
        self.connected = False

        self.timer = QTimer()
        
        self.server = QLocalServer()
        QLocalServer.removeServer('doorbotgui')
        
        if not self.server.listen('doorbotgui'):
            print(self.server.errorString())
            return

        botlog.info('SocketServerThread Initialized.')
        
    def __del__(self):
        botlog.info('SocketServer Thread Deletion')

    def onTimer(self):
        if self.connected:
            self.sendCurrentTime()
        
    def sendPacket(self, pkt):
        if self.connected:
            try:
                self.client.write(json.dumps(pkt) + '\n')
                self.client.flush()
            except:
                print('could not sendPacket')

    def sendReadStatus(self):
        pkt = {'cmd':'readstatus', 'status':str(self.readerThread.status)}
        self.sendPacket(pkt)

    def sendAccess(self, allowed, memberData):
        pkt = {'cmd':'access', 'result':allowed, 'member':memberData}
        self.sendPacket(pkt)

    def sendCurrentTime(self):
        pkt = {'cmd':'time', 'time':datetime.now().strftime("%A, %d %B %Y %H:%M:%S")}
        self.sendPacket(pkt)

    def onStatusChange(self, status):
        self.sendReadStatus()

    def onAccess(self, allowed, memberData):
        self.sendAccess(allowed, memberData)
        
    def onConnect(self):
        botlog.info('New connection to SocketServer')

        try:
            self.client = self.server.nextPendingConnection()
            self.client.disconnected.connect(self.onDisconnect)

        except:
            botlog.error('exception creating client')

        self.connected = True
            
        self.sendReadStatus()

    def onDisconnect(self):
        self.connected = False
        self.client.deleteLater()
        botlog.info('SocketServer disconnected')
        
    def run(self):
        botlog.info('SocketServer Thread Running')

        if self.readerThread:
            self.readerThread.signalStatusChange.connect(self.onStatusChange)
            self.readerThread.signalAccess.connect(self.onAccess)
        
        self.server.newConnection.connect(self.onConnect)

        self.timer.timeout.connect(self.onTimer)
        self.timer.start(1000)
        
        self.exec()
        botlog.info('SocketServerThread Stopped.')

        
class RFIDReaderThread(QThread):
    signalStatusChange = pyqtSignal(Status)
    signalAccess = pyqtSignal('QString', dict)
    
    def __init__(self, parent=None):
        QThread.__init__(self, parent)

        self.status = Status.INIT
        
        self.reader = rfid_reader.factory(qsetup.READER_TYPE)
        self.reader.initialize(baud_rate=qsetup.READER_BAUD_RATE, serial_port=qsetup.READER_DEVICE)

        self.authenticate = Authenticate.factory(qsetup.AUTHENTICATE_TYPE, qsetup.AUTHENTICATE_FILE)

        botlog.info('authentication file date %s' % self.authenticate.get_file_time())
        botlog.info('RFIDReaderThread Initialized.')
        
    def __del__(self):
        botlog.info('RFIDReaderThread Thread Deletion.')
        self.wait()

    def setStatus(self, s):
        botlog.debug('status change from %s to %s' % (self.status, s))
        self.status = s
        self.signalStatusChange.emit(s)
        
    def undelay(self):
        botlog.debug('undelay')
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
        # 3. good card, allowed - grant access
        # 4. bad card from some reason
        # 5. unknown card
        try :
            self.setStatus(Status.READING)
            rfid = int(rfid_str)
            
            access = self.authenticate.get_access(rfid)
                    
            if access:
                allowed = access['allowed']
                member = access['member']
                plan = access['plan']
                
                print(allowed)
                print(access)
                print(plan)
                
                if 'allowed' in allowed :
                    # 3. grant access
                    #
                    botlog.info('%s allowed' % member)
                    
                    self.setStatus(Status.ALLOWED)
                    self.notifier.setEnabled(False)
                    self.delayTimer.stop()
                    self.delayTimer.start(2000)

                else :
                    #2
                    # access failed.
                    botlog.warning('%s DENIED' % member)
                    self.setStatus(Status.DENIED)
                    self.notifier.setEnabled(False)
                    self.delayTimer.stop()
                    self.delayTimer.start(2000)

            else :
                #5
                botlog.warning('Unknown card %s ' % rfid_str)
                self.setStatus(Status.UNKNOWN)
                self.signalAccess.emit('denied', {'member':'Unknown.RFID.Tag', 'plan':None, 'tagid':'', 'allowed':'denied', 'nickname':None, 'warning':'This RFID tag is not recognized.  Be sure you are using the correct tag and hold it steady over the read antenna.\n\nContact board@makeitlabs.com if you continue to have problems.'})

                self.notifier.setEnabled(False)
                self.delayTimer.stop()
                self.delayTimer.start(3000)

            if access and allowed:
                self.signalAccess.emit(allowed, access)


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
        botlog.info('RFIDReaderThread Running.')

        self.delayTimer = QTimer()
        self.delayTimer.timeout.connect(self.undelay)
        self.delayTimer.setSingleShot(True)
        
        self.notifier = QSocketNotifier(self.reader.fileno(), QSocketNotifier.Read)
        self.notifier.activated.connect(self.onData)
        
        self.setStatus(Status.READY)
        self.exec()
        
        botlog.info('RFIDReaderThread Stopped.')


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    
    app = QCoreApplication(sys.argv)
    
    rfid = RFIDReaderThread()
    server = SocketServerThread(readerThread=rfid)

    
    rfid.start()
    server.start()
    
    app.exec()