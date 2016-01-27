import sys
import signal
import json
from datetime import datetime, date, time
from PyQt4 import QtGui
from PyQt4.QtWebKit import QWebView
from PyQt4.QtCore import Qt, QUrl, QTimer
from PyQt4.QtGui import QApplication, QCursor, QPalette
from PyQt4.QtNetwork import QLocalSocket

def sigint_handler(*args):
    QApplication.quit()

class DoorbotGUI(QtGui.QWidget):
    
    def __init__(self):
        self.dispatchTable = {
            'heartbeat' : self.respHeartBeat,
            'time' : self.respTime,
            'access' : self.respAccess
        }

        
        self.timer = QTimer()
        self.name = QtGui.QLabel()
        self.plan = QtGui.QLabel()
        self.warning = QtGui.QLabel()
        self.status1 = QtGui.QLabel()
        self.status2 = QtGui.QLabel()
        self.status3 = QtGui.QLabel()
        super(DoorbotGUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.reconnectTimer = QTimer()
        self.reconnectTimer.timeout.connect(self.onReconnect)
        self.reconnectTimer.stop()
        
        self.socket = QLocalSocket()
        self.socket.connected.connect(self.onConnect)
        self.socket.disconnected.connect(self.onDisconnect)
        self.socket.readyRead.connect(self.onReadyRead)
        self.socket.error.connect(self.onError)
        self.socket.connectToServer('doorbotgui')
        
        #web = QWebView()
        #web.load(QUrl('http://www.google.com/'))
        
        box = QtGui.QVBoxLayout()
        box.setSpacing(10)
        box.setAlignment(Qt.AlignCenter)

        box.addWidget(self.name)
        box.addWidget(self.plan)
        box.addWidget(self.warning)
        self.warning.setWordWrap(True)
        box.addStretch(1)
        box.addWidget(self.status1)
        box.addWidget(self.status2)
        box.addWidget(self.status3)

        #box.addWidget(web)
        
        self.setLayout(box) 

        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

        self.statusDisplayCount = 0
        
        self.setCursor(Qt.BlankCursor)
        self.showFullScreen()
        self.show()
        
    def tick(self):
        if self.statusDisplayCount > 0:
            self.statusDisplayCount = self.statusDisplayCount - 1
            if self.statusDisplayCount == 0:
                self.status1.setText('Please scan your RFID Below')
                self.name.setText('')
                self.plan.setText('')
                self.warning.setText('')
                p = self.palette()
                p.setColor(self.backgroundRole(), Qt.gray)
                self.setPalette(p)
                

    def onReconnect(self):
        self.reconnectTimer.stop()
        self.status2.setText('reconnecting')
        self.socket.connectToServer('doorbotgui')
        
    def onConnect(self):
        self.status2.setText('connected')
        
    def onDisconnect(self):
        self.status2.setText('disconnected')
        self.reconnectTimer.start(2000)

    def onError(self, err):
        self.status2.setText('error ' + self.socket.errorString() )
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
        self.status2.setText('heartbeat %d' % pkt['count'])

    def respTime(self, pkt):
        self.status3.setText(pkt['time'])

    def respAccess(self, pkt):
        result = pkt['result']
        if 'member' in pkt:
            member = pkt['member']
            
            self.name.setText(member['member'])
            self.plan.setText(member['plan'])
            self.warning.setText(member['warning'])
            
            p = self.palette()
            if result == 'allowed':
                if not member['warning'] == '':
                    p.setColor(self.backgroundRole(), Qt.yellow)
                else:
                    p.setColor(self.backgroundRole(), Qt.green)

                self.status1.setText('Welcome')

            elif result == 'denied':
                self.status1.setText('Access Denied')
                p.setColor(self.backgroundRole(), Qt.red)

            self.setPalette(p)
            self.statusDisplayCount = 5
        
def main():
    signal.signal(signal.SIGINT, sigint_handler)
    
    app = QApplication(sys.argv)
    ex = DoorbotGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
                                                                                            
