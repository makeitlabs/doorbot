from PyQt5.QtCore import QThread, QCoreApplication, QTimer, QSocketNotifier, pyqtSignal, pyqtSlot, QByteArray
from PyQt5.QtNetwork import QLocalServer

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
from qdoor_hw import DoorHW
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
    LATCHED = 6
    ERROR = 7

class SocketServerThread(QThread):
    def __init__(self, parent=None, readerThread=None):
        QThread.__init__(self, parent)

        self.readerThread = readerThread;
        self.connected = False

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
            self.sendCurrentSchedule()

    def sendPacket(self, pkt):
        if self.connected:
            p = json.dumps(pkt) + '\n'
            bytes = QByteArray(p.encode())
            try:
                self.client.write(bytes)
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

    def sendCurrentSchedule(self):
        pkt = {'cmd':'schedule', 'description':qsetup.schedule.scheduleDesc()}
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
        self.sendCurrentSchedule()

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

        self.timer = QTimer()
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(1000)

        self.exec()
        botlog.info('SocketServerThread Stopped.')

class RFIDReaderThread(QThread):
    signalStatusChange = pyqtSignal(Status)
    signalAccess = pyqtSignal('QString', dict)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

        self.latchTimer = QTimer()
        self.delayTimer = QTimer()


        self.status = Status.INIT

        self.hw = DoorHW(red_pin=qsetup.RED_PIN, green_pin=qsetup.GREEN_PIN, door_pin=qsetup.DOOR_PIN, beep_pin=qsetup.BEEP_PIN)

        self.reader = rfid_reader.factory(qsetup.READER_TYPE)
        self.reader.initialize(baud_rate=qsetup.READER_BAUD_RATE, serial_port=qsetup.READER_DEVICE)

        self.authenticate = Authenticate.factory(qsetup.AUTHENTICATE_TYPE, qsetup.AUTHENTICATE_FILE)

        botlog.info('authentication file date %s' % self.authenticate.get_file_time())
        botlog.info('RFIDReaderThread Initialized.')

        self.notifier = QSocketNotifier(self.reader.fileno(), QSocketNotifier.Read)



    def __del__(self):
        botlog.info('RFIDReaderThread Thread Deletion.')
        self.wait()

    def updateLEDs(self):
        if self.status == Status.INIT:
            self.hw.green(on=True)
            self.hw.red(on=True)
            self.hw.beep(on=False)
        elif self.status == Status.READY:
            self.hw.green(on=self.blinkPhase)
            self.hw.red(on=False)
            self.hw.beep(on=False)
        elif self.status == Status.DENIED or self.status == Status.UNKNOWN:
            self.hw.green(on=False)
            self.hw.red(on=True)
            self.hw.beep(on=True)
        elif self.status == Status.ALLOWED or self.status == Status.LATCHED:
            self.hw.green(on=True)
            self.hw.red(on=False)
            self.hw.beep(on=False)
        elif self.status == Status.ERROR or self.status == Status.UNKNOWN:
            self.hw.green(on=False)
            self.hw.red(on=self.blinkPhase)
            self.hw.beep(on=False)

    def blink(self):
        self.updateLEDs()
        self.blinkPhase = not self.blinkPhase

    def setStatus(self, s):
        botlog.debug('status change from %s to %s' % (self.status, s))
        self.status = s
        self.signalStatusChange.emit(s)
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
        # 3. good card, allowed:
        # 3a.  schedule permits access at this time, so open door
        # 3b.  schedule does not permit access at this time.
        # 4. bad card from some reason
        # 5. unknown card
        try :
            self.setStatus(Status.READING)
            rfid = int(rfid_str)

            access = self.authenticate.get_access(rfid)

            allowed = 'false'
            member = ''
            plan = ''
            if access:
                allowed = access['allowed']
                member = access['member']
                plan = access['plan']

                print(allowed)
                print(access)
                print(plan)

                if 'allowed' in allowed :
                    if qsetup.schedule.isAllowed(plan):
                        # 3a. open the door
                        #
                        botlog.info('%s allowed' % member)

                        self.setStatus(Status.ALLOWED)
                        self.setStatus(Status.LATCHED)

                        self.hw.latch(open=True)
                        self.notifier.setEnabled(False)
                        self.latchTimer.start(4000)
                    else:
                        # 3b. denied due to local schedule
                        botlog.warning('%s DENIED due to schedule restriction' % member)

                        allowed = 'denied'

                        if member['warning'] is None or member['warning'] == '':
                            member['warning'] = qsetup.schedule.scheduleDesc()
                        else:
                            member['warning'] += '\n%s' % qsetup.schedule.scheduleDesc()

                        self.setStatus(Status.DENIED)
                        self.notifier.setEnabled(False)
                        self.delayTimer.start(2000)
                else :
                    #2
                    # access failed.  blink the red
                    #
                    botlog.warning('%s DENIED' % member)
                    self.setStatus(Status.DENIED)
                    self.notifier.setEnabled(False)
                    self.delayTimer.start(2000)


            else :
                #5
                botlog.warning('Unknown card %s ' % rfid_str)
                self.setStatus(Status.UNKNOWN)
                access = {'member':'Unknown.RFID.Tag', 'plan':None, 'tagid':'', 'allowed':'denied', 'nickname':None, 'warning':'This RFID tag is not recognized.  Be sure you are using the correct tag and hold it steady over the read antenna.\n\nContact board@makeitlabs.com if you continue to have problems.'}
                self.signalAccess.emit('denied', access)

                self.notifier.setEnabled(False)
                self.delayTimer.start(2000)

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

        self.notifier.activated.connect(self.onData)

        self.latchTimer.timeout.connect(self.unlatch)
        self.latchTimer.setSingleShot(True)

        self.delayTimer.timeout.connect(self.undelay)
        self.delayTimer.setSingleShot(True)


        self.blinkTimer = QTimer()
        self.blinkPhase = False
        self.blinkTimer.timeout.connect(self.blink)

        self.blinkTimer.start(250)
        self.notifier.setEnabled(True)

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
