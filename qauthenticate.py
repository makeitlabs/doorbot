import sys
import os
import re
import hashlib
import qsetup
from qsetup import botlog

# base class
class Authenticate():
    @staticmethod
    def factory(t, filename):
        if t == 'csv':
            return AuthenticateCSV(filename)
        elif t == 'json':
            return AuthenticateJSON(filename)
        assert 0, 'bad authentication type ' + t

    def __init__(self, filename):
        self.filename = filename
    
    def load(self):
        pass

    def reload(self):
        pass

    def get_access(self, rfid):
        pass

    def test(self) :
        print('TEST card_data has %d entries' % len(self.card_data))

        print()
        test_tag = '0004134419'
        a = self.get_access(int(test_tag))
        print('TEST %s\n%s' % (test_tag, a))

        a = self.get_access(1258648)
        print('TEST 1258648')
        print(a)

        print('TEST 1234 %s' % self.get_access(1234))


# CSV formatted ACL file
class AuthenticateCSV(Authenticate):
    def __init__(self, filename):
        Authenticate.__init__(self, filename)

        print('AuthenticateCSV init filename=%s' % self.filename)

        self.card_data = {}
        
        # tracks file updates
        self.file_time = 0

        # regex to match a csv line that includes ,, fields and "a,b,c" nested commas
        # http://stackoverflow.com/questions/18144431/regex-to-split-a-csv
        self.csv_regexp = re.compile(r'(?:^|,)(?=[^"]|(")?)"?((?(1)[^"]*|[^,"]*))"?(?=,|$)')

        self.reload()

    def load(self):
        "return a dictionary of (username,key,allowed) indexed by hashed rfid"

        try:
            f = open(self.filename)
            lines = f.read().splitlines()
            f.close()
        except:
            botlog.critical( "authenticate can't read CSV %s" % self.filename)
            return {}
    
        cd = {}
        for l in lines[1:] :
            try :
                (member,value,key,allowed,tagid,lastAccessed) = [x[1] for x in self.csv_regexp.findall(l)]

                cd[tagid] = {'member': member, 'allowed': allowed, 'tagid':tagid, 'warning':None, 'plan':None, 'nickname':None}

            except:
                botlog.error( 'authenticate CSV fail: %s %s' % (l, sys.exc_info()))

        botlog.info( "authenticate read CSV %s %d entries" % (self.filename, len(cd)))
        return cd

    def reload(self) :
        "check the file and reload data if needed"

        try:
            fd = os.open(self.filename, os.O_RDONLY)
            fi = os.fstat(fd)
            os.close(fd)

            if fi.st_mtime > self.file_time :
                self.card_data = self.load()
                self.file_time = fi.st_mtime
        except OSError as e:
            botlog.critical( "authenticate failure on file %s: %s" % (self.filename, e.strerror))
        except:
            botlog.critical( "authenticate exception on file %s" % self.filename)
    
    def get_access(self, rfid) :
        "given an integer rfid card number, return None or a tuple of (username,allowed)"

        self.reload()

        # hash the RFID key.  legacy stuff from original circa 2011 system.  becausejoe.        
        m = hashlib.sha224()
        rfidStr = "%.10d"%(int(rfid))
        m.update(str(rfidStr).encode())
        rfid_hash = m.hexdigest()
        
        botlog.debug( 'rfid_hash: %s' % rfid_hash)


        if rfid_hash not in self.card_data :
            return None

        return self.card_data[rfid_hash]


if __name__ == '__main__':
    # test
    a = Authenticate.factory('csv', qsetup.AUTHENTICATE_CSV_FILE)
    a.test()
