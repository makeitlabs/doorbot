import sys
import os
import re
import hashlib
import qsetup
import json
import time
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
        self.card_data = {}

        self.filename = filename

        # tracks file updates
        self.file_time = 0

    def get_file_time(self):
        return time.ctime(self.file_time)
    
    def get_raw_file_time(self):
        try:
            fd = os.open(self.filename, os.O_RDONLY)
            fi = os.fstat(fd)
            os.close(fd)
            return time.ctime(fi.st_mtime)
                
        except OSError as e:
            botlog.critical( "get_file_time exception on file %s: %s" % (self.filename, e.strerror))
        except:
            botlog.critical( "get_file_time exception on file %s: %s" % (self.filename, sys.exc_info()))

        return 'get_file_time err'

    def load(self):
        pass

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
            botlog.critical( "reload exception on file %s: %s" % (self.filename, e.strerror))
        except:
            botlog.critical( "reload exception on file %s: %s" % (self.filename, sys.exc_info()))
    
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

        
# JSON formatted ACL file (API ACL format v1)
class AuthenticateJSON(Authenticate):
    def __init__(self, filename):
        Authenticate.__init__(self, filename)

        self.reload()

    def load(self):
        "return a dictionary of dictionaries with member info indexed by hashed rfid"

        cd = {}
        try:
            with open(self.filename) as json_file:
                json_data = json.load(json_file)
            
            for member in json_data:
                cd[member['tagid']] = member
                
        except:
            botlog.error('exception loading JSON ACL %s: %s' % (self.filename, sys.exc_info()))

        return cd
        
        
# CSV formatted ACL file (API ACL format v0)
class AuthenticateCSV(Authenticate):
    def __init__(self, filename):
        Authenticate.__init__(self, filename)

        # regex to match a csv line that includes ,, fields and "a,b,c" nested commas
        # http://stackoverflow.com/questions/18144431/regex-to-split-a-csv
        self.csv_regexp = re.compile(r'(?:^|,)(?=[^"]|(")?)"?((?(1)[^"]*|[^,"]*))"?(?=,|$)')

        self.reload()

    def load(self):
        "return a dictionary of dictionaries with member info indexed by hashed rfid"

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



if __name__ == '__main__':
    # test
    c = Authenticate.factory('csv', qsetup.AUTHENTICATE_CSV_FILE)
    c.test()

    j = Authenticate.factory('json', qsetup.AUTHENTICATE_JSON_FILE)
    j.test()
