import sys
import signal
import json
from datetime import datetime, date, time
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtNetwork import QLocalServer

def sigint_handler(*args):
    QCoreApplication.quit()

class GUIServer():
    
    def __init__(self):
        self.heartbeats = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(500)
        
        self.server = QLocalServer()
        if not self.server.listen('doorbotgui'):
            print(self.server.errorString())
            #self.close()
            return

        self.server.newConnection.connect(self.handleConnection)
        
        super(GUIServer, self).__init__()


    def handleConnection(self):
        self.client = self.server.nextPendingConnection()
        self.client.disconnected.connect(self.client.deleteLater)
        self.client.write("Hello")
        self.client.flush()


    def sendPacket(self, pkt):
        try:
            self.client.write(json.dumps(pkt) + '\n')
        except:
            print('could not sendPacket')
        
    def tick(self):

        self.heartbeats = self.heartbeats + 1

        if self.heartbeats % 10 == 0:
            heartbeat = {'cmd':'heartbeat', 'count': self.heartbeats}
            self.sendPacket(heartbeat)

        if self.heartbeats % 33 == 0:
            access = {'cmd':'access', 'result':'allowed',
                      'member':{"tagid": "12345", "member": "Johnathan.Smith", "warning": "", "plan": "pro", "allowed": "allowed", "nickname": "Captain of the Starship Pi"}
            }
            self.sendPacket(access)

        if self.heartbeats % 44 == 0:
            access = {'cmd':'access', 'result':'denied',
                      'member':{"tagid": "abcde", "member": "Al.Johnson", "warning": "Your membership expired (2012-07-02T00:04:25Z) and the grace period for access has ended. Contact board@makeitlabs.com with any questions.", "plan": "hobbyist", "allowed": "denied", "nickname": None}
            }
            self.sendPacket(access)

        if self.heartbeats % 55 == 0:
            access = {'cmd':'access', 'result':'allowed',
                      'member':{"tagid": "123abc", "member": "Michael.Michaelson", "warning": "You do not have access to this resource. See the Wiki for training information and resource manager contact info.", "plan": "hobbyist", "allowed": "denied", "nickname": None}
            }
            self.sendPacket(access)
            
        time = {'cmd':'time', 'time':datetime.now().strftime("%A, %d %B %Y %H:%M:%S")}
        self.sendPacket(time)

        
def main():
    signal.signal(signal.SIGINT, sigint_handler)
    
    app = QCoreApplication(sys.argv)
    
    ex = GUIServer()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
                                                                                            
