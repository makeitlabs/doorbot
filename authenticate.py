
import re
import hashlib



card_data_file = 'databases/door.csv'


####




# regex to match a csv line that includes ,, fields and "a,b,c" nested commas
# http://stackoverflow.com/questions/18144431/regex-to-split-a-csv
#
csv_line = re.compile(r'(?:^|,)(?=[^"]|(")?)"?((?(1)[^"]*|[^,"]*))"?(?=,|$)')



def read_card_data(csv_filename) :
    "return a dictionary of (username,key,allowed) indexed by hashed rfid"

    f = open(csv_filename)
    lines = f.read().splitlines()
    f.close()
    
    cd = {}
    for l in lines[1:] :
        try :
            (hashedCard,username,allowed) = [x[1] for x in csv_line.findall(l)]
            # throw away value(?) and lastAccessed
            cd[hashedCard] = (username,allowed)
        except :
            print 'CSV fail: %s' % l
    return cd

card_data = read_card_data(card_data_file)




def get_access(rfid) :
    "given an integer rfid card number, return None or a tuple of (username,allowed)"

    m = hashlib.sha224()

    # don't ask.  this is the way it was done so we have to also
    #becausejoe
    #
    rfidStr = "%.10d"%(int(rfid))
    m.update(str(rfidStr).encode())

    
    rfid_hash = m.hexdigest()
    print rfid_hash

    if rfid_hash not in card_data :
        return None

    return card_data[rfid_hash]


def test() :

    print
    test_tag = '0004134419'
    a = get_access(int(test_tag))
    print a

    a = get_access(1258648)
    print a


    print get_access(1234)
        


if __name__ == '__main__':
    test()
