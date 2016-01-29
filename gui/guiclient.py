import sys
import signal
import json
from datetime import datetime, date, time

from PyQt4 import QtGui
from PyQt4.QtWebKit import QWebView
from PyQt4.QtCore import Qt, QUrl, QTimer
from PyQt4.QtGui import QApplication, QWidget, QDialog, QCursor, QPalette, QDesktopWidget
from PyQt4.QtNetwork import QLocalSocket

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
        cp = QtGui.QDesktopWidget().availableGeometry().center()
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


        if member['nickname'] != None:
            self.labelName.setText(member['nickname'])
        else:
            self.labelName.setText(member['member'])
            
        self.labelPlan.setText(member['plan'])

        if member['warning'] == '':
            self.labelWarning.setText('Welcome to MakeIt Labs!  Enjoy your visit.')
        else:
            self.labelWarning.setText(member['warning'])
        self.timer.start(5000)
        self.open()


class DoorbotGUI(QWidget, Ui_BotGUI):
    
    def __init__(self):
        QWidget.__init__(self)

        self.setupUi(self)

        self.accessDialog = AccessDialog(self)
        self.accessDialog.hide()
        
        self.dispatchTable = {
            'heartbeat' : self.respHeartBeat,
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
        print('tick')

                

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
                print('could not dispatch')
                

    def respHeartBeat(self, pkt):
        # TODO: track and add timeout
        self.heartbeats = pkt['count']

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
        self.labelReadStatus.setText(status)
        
        
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
                                                                                            
