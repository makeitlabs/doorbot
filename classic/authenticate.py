import os
import re
import hashlib
import setup
from setup import botlog


card_data_file = setup.card_data_file # 'databases/door.csv'

card_data = {}


####

# used to re-read a new file
#
file_time = 0



# regex to match a csv line that includes ,, fields and "a,b,c" nested commas
# http://stackoverflow.com/questions/18144431/regex-to-split-a-csv
#
csv_line = re.compile(r'(?:^|,)(?=[^"]|(")?)"?((?(1)[^"]*|[^,"]*))"?(?=,|$)')



def read_card_data(csv_filename) :
    "return a dictionary of (username,key,allowed) indexed by hashed rfid"

    try :
        f = open(csv_filename)
        lines = f.read().splitlines()
        f.close()
    except :
        botlog.critical( "authenticate can't read CSV %s" % csv_filename)
        return {}
    
    cd = {}
    for l in lines[1:] :
        try :
            (username,value,key,allowed,hashedCard,lastAccessed) = [x[1] for x in csv_line.findall(l)]
            # throw away value(?) and lastAccessed
            cd[hashedCard] = (username,allowed)

        except :
            botlog.error( 'authenticate CSV fail: %s' % l)

    botlog.info( "authenticate read CSV %s %d entries" % (csv_filename, len(cd)))
    return cd


def re_read_file(csv_filename=card_data_file) :
    "check the file and reload data if needed"

    global card_data
    global file_time


    try :
        fd = os.open(csv_filename,os.O_RDONLY)
        fi = os.fstat(fd)
        os.close(fd)

        if fi.st_mtime > file_time :
            card_data = read_card_data(csv_filename)
            file_time = fi.st_mtime
    except :
        botlog.critical( "authenticate can't fstat CSV %s" % csv_filename)
    




# check for empty tag dict?
re_read_file()


def get_access(rfid) :
    "given an integer rfid card number, return None or a tuple of (username,allowed)"

    re_read_file()

    m = hashlib.sha224()

    # don't ask.  this is the way it was done so we have to also
    #becausejoe
    #
    rfidStr = "%.10d"%(int(rfid))
    m.update(str(rfidStr).encode())

    
    rfid_hash = m.hexdigest()
    botlog.debug( 'rfid_hash: %s' % rfid_hash)


    if rfid_hash not in card_data :
        return None

    return card_data[rfid_hash]


def test() :

    print 'card_data %d' % len(card_data)

    print
    test_tag = '0004134419'
    a = get_access(int(test_tag))
    print a

    a = get_access(1258648)
    print a


    print get_access(1234)
        


if __name__ == '__main__':
    test()
