

# base class for rfid reader, also default of HID reader
#
# first version is blocking.  probably will eventually return immediatly with None or a card string
#

class rfid_reader() :

    def initialize(self) :
        pass

    def get_card(self) :
        return None

class rfid_reader_hid(rfid_reader) :

    def get_card(self) :
        return raw_input('input rfid? ')




