import sys
import signal
import json
from datetime import datetime, date, time

from PyQt4 import QtGui
from PyQt4.QtWebKit import QWebView
from PyQt4.QtCore import Qt, QUrl, QTimer
from PyQt4.QtGui import QApplication, QWidget, QCursor, QPalette
from PyQt4.QtNetwork import QLocalSocket

# to rebuild ui file with PyQt4:
# pyuic4 bot.ui -o ui_bot.py
# 
from ui_bot import Ui_BotGUI

def sigint_handler(*args):
    QApplication.quit()

class DoorbotGUI(QWidget, Ui_BotGUI):
    
    def __init__(self):
        QWidget.__init__(self)

        #uic.loadUi('bot.ui', self)
        
        self.setupUi(self)
        
        self.dispatchTable = {
            'heartbeat' : self.respHeartBeat,
            'time' : self.respTime,
            'access' : self.respAccess
        }
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        self.statusDisplayCount = 0

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
        if self.statusDisplayCount > 0:
            self.statusDisplayCount = self.statusDisplayCount - 1
            if self.statusDisplayCount == 0:
                self.labelStatus1.setText('Please scan your RFID Below')
                self.labelName.setText('')
                self.labelPlan.setText('')
                self.labelWarning.setText('')
                p = self.labelWarning.palette()
                p.setColor(self.backgroundRole(), Qt.black)
                self.labelWarning.setPalette(p)
                

    def onReconnect(self):
        self.reconnectTimer.stop()
        self.labelStatus2.setText('reconnecting')
        self.socket.connectToServer('doorbotgui')
        
    def onConnect(self):
        self.labelStatus2.setText('connected')
        
    def onDisconnect(self):
        self.labelStatus2.setText('disconnected')
        self.reconnectTimer.start(2000)

    def onError(self, err):
        self.labelStatus2.setText('error ' + self.socket.errorString() )
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
        self.labelStatus2.setText('heartbeat %d' % pkt['count'])

    def respTime(self, pkt):
        self.labelStatus3.setText(pkt['time'])

    def respAccess(self, pkt):
        result = pkt['result']
        if 'member' in pkt:
            member = pkt['member']
            
            self.labelName.setText(member['member'])
            self.labelPlan.setText(member['plan'])

            if not member['warning'] == '':
                self.labelWarning.setText(member['warning'])
            else:
                self.labelWarning.setText('Welcome to MakeIt Labs!')
                
            p = self.labelWarning.palette()
            if result == 'allowed':
                if not member['warning'] == '':
                    p.setColor(self.foregroundRole(), QColor(0xcc, 0x7c, 0x2b))
                else:
                    p.setColor(self.foregroundRole(), Qt.green)

                self.status1.setText('Welcome')

            elif result == 'denied':
                self.labelStatus1.setText('Access Denied')
                p.setColor(self.foregroundRole(), Qt.red)

            self.labelWarning.setPalette(p)
            self.statusDisplayCount = 5
        
def main():
    signal.signal(signal.SIGINT, sigint_handler)
    
    app = QApplication(sys.argv)
    ex = DoorbotGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
                                                                                            
