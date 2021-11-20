import sys
import signal
from subprocess import check_output
import json
from datetime import datetime, date, time

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import QLocalSocket

# to build ui and resources file with PyQt4:
# pyuic4 bot.ui -o ui_bot.py
# pyuic4 access.ui -o ui_access.py
# pyrcc4 -py3 icons.qrc -o icons_rc.py
#
#
from ui_bot import Ui_BotGUI
from ui_access import Ui_AccessDialog

def sigint_handler(*args):
    QApplication.quit()


class AccessDialog(QDialog, Ui_AccessDialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)

        self.setupUi(self)

        self.timer = QTimer()
        self.timer.timeout.connect(self.hide)

        self.setWindowFlags(Qt.FramelessWindowHint)

        fg = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())

    def memberAccess(self, result, member):
        if result == 'allowed':
            if member['warning'] == '':
                self.frameLeftBar.setStyleSheet('background-color: rgb(26,185,18);')
            else:
                self.frameLeftBar.setStyleSheet('background-color: rgb(255,226,58);')

        elif result == 'denied':
            self.frameLeftBar.setStyleSheet('background-color: rgb(185,26,18);')

        if member['nickname'] is not None:
            self.labelName.setText(member['nickname'])
        else:
            self.labelName.setText(member['member'].replace('.', ' '))

        if not 'plan' in member or member['plan'] is None:
            self.labelPlan.setVisible(False)
        elif 'pro' in member['plan']:
            self.labelPlan.setVisible(True)
            self.labelPlan.setText('Professional Member')
        elif 'hobby' in member['plan']:
            self.labelPlan.setVisible(True)
            self.labelPlan.setText('Hobbyist Member')
        else:
            self.labelPlan.setVisible(True)
            self.labelPlan.setText('Member')

        if result == 'allowed' and member['warning'] == '':
            self.labelWarning.setText('Welcome to MakeIt Labs!  Enjoy your visit.')
        else:
            self.labelWarning.setText(member['warning'])

        if 'last_accessed' in member and member['last_accessed'] is not None:
            self.labelLastVisit.setVisible(True)
            self.labelLastVisit.setText('Last visit on %s' % member['last_accessed'])
        else:
            self.labelLastVisit.setVisible(False)
            self.labelLastVisit.setText('')

        self.timer.start(5000)
        self.open()


class DoorbotGUI(QWidget, Ui_BotGUI):

    def __init__(self):
        QWidget.__init__(self)

        self.setupUi(self)

        self.accessDialog = AccessDialog(self)
        self.accessDialog.hide()

        self.dispatchTable = {
            'time' : self.respTime,
            'schedule' : self.respSchedule,
            'bulletin' : self.respBulletin,
            'readstatus' : self.respReadStatus,
            'access' : self.respAccess
        }

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

        self.reconnectTimer = QTimer()
        self.reconnectTimer.timeout.connect(self.onReconnect)
        self.reconnectTimer.stop()

        self.socket = QLocalSocket()
        self.socket.connected.connect(self.onConnect)
        self.socket.disconnected.connect(self.onDisconnect)
        self.socket.readyRead.connect(self.onReadyRead)
        self.socket.error.connect(self.onError)
        self.socket.connectToServer('doorbotgui')


        self.setCursor(Qt.BlankCursor)
        self.showFullScreen()
        self.show()

    def tick(self):
        pass

    def onReconnect(self):
        self.reconnectTimer.stop()
        self.labelHealth.setText('Reconnecting to backend.')
        self.socket.connectToServer('doorbotgui')

    def onConnect(self):
        self.labelHealth.setText('Connected to backend.')

    def onDisconnect(self):
        self.labelHealth.setText('Disconnected from backend.')
        self.reconnectTimer.start(2000)

    def onError(self, err):
        self.labelHealth.setText('Backend connect error ' + self.socket.errorString() + '.' )
        self.reconnectTimer.start(2000)

    def onReadyRead(self):
        while self.socket.canReadLine():
            rx = self.socket.readLine(2048).decode('utf-8')
            try:
                pkt = json.loads(rx)
                print(pkt)

                cmd = pkt['cmd']

                if cmd in self.dispatchTable:
                    self.dispatchTable[cmd](pkt)
            except ValueError:
                print('could not decode json')

            except:
                print('could not dispatch: %s', sys.exc_info())

    def respTime(self, pkt):
        self.labelTime.setText(pkt['time'])

    def respSchedule(self, pkt):
        desc = pkt['description']
        self.labelSchedule.setText(desc)

    def respBulletin(self, pkt):
        source = pkt['source']

        self.textBrowser.setSource(QUrl(source))
        self.textBrowser.reload()

    def respReadStatus(self, pkt):
        status = pkt['status']

        if status == 'Status.INIT':
            statusText = 'Initializing System.'
        elif status == 'Status.READY':
            statusText = 'Please scan your tag below.'
        elif status == 'Status.READING':
            statusText = 'Reading tag...'
        elif status == 'Status.DENIED':
            statusText = 'Access denied.'
        elif status == 'Status.ALLOWED' or status == 'Status.LATCHED':
            statusText = 'Access granted.'
        elif status == 'Status.UNKNOWN':
            statusText = 'Tag not recognized.'
        elif status == 'Status.ERROR':
            statusText = 'An unexpected error has occurred.  Contact board@makeitlabs.com.'
        else:
            statusText = 'Unexpected status: %s' % status

        self.labelReadStatus.setText(statusText)


    def respAccess(self, pkt):
        result = pkt['result']
        member = pkt['member']

        self.accessDialog.memberAccess(result, member)

def main():
    signal.signal(signal.SIGINT, sigint_handler)

    app = QApplication(sys.argv)
    ex = DoorbotGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
