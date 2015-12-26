import serial
import sys
import time

##from operator import xor


# base class for rfid reader, also default of HID reader
#
# first version is blocking.  probably will eventually return immediatly with None or a card string
#

class rfid_reader() :

    def initialize(self) :
        pass

    def get_card(self) :
        return None

    def flush(self) :
        pass



class rfid_reader_hid(rfid_reader) :

    def get_card(self) :
        return raw_input('input rfid? ')

    def flush(self) :
        pass


# Flags
Startflag = "\x02"
Endflag = "\x03"

class rfid_reader_serial() :

    def __init__(self) :
        # self.ID = ""
        # self.Zeichen = 0
        # self.Checksumme = 0
        # self.Tag = 0
        pass


    def initialize(self, serial_port="/dev/ttyAMA0", baud_rate=9600) :

        print 'br=%d' % baud_rate
        # Open UART (close first just to make sure)
        #
        self.UART = serial.Serial(serial_port, baud_rate)
        self.UART.close()
        self.UART.open()


    def flush(self) :
#        self.UART.reset_input_buffer()
        self.UART.flushInput()  # Deprecated since version 3.0: see reset_input_buffer()


    def get_card(self) :

        if not self.UART.inWaiting() :
            return None

        # Reset vars
        Checksumme = 0
        Checksumme_Tag = 0
        ID = ""

        # Read chars
        Zeichen = self.UART.read()
        # Start of transmission signaled?

        if Zeichen != Startflag:
            self.flush()
            return None

        # Build ID
        for Counter in range(13):
            Zeichen = self.UART.read()
            ID = ID + str(Zeichen)
            # Remove endflag from string
        ID = ID.replace(Endflag, "" )


        # Calc checksum
        for I in range(0, 9, 2):
            Checksumme = Checksumme ^ (((int(ID[I], 16)) << 4) + int(ID[I+1], 16))
        Checksumme = hex(Checksumme)
        # Find tag
        Tag = ((int(ID[1], 16)) << 8) + ((int(ID[2], 16)) << 4) + ((int(ID[3], 16)) << 0)
        Tag = hex(Tag)
        # Print data

        card = str(int(ID[4:10], 16))
        print "------------------------------------------"
        print "Data: ", ID
        print "Tag: ", Tag
        print "ID: ", ID[4:10], " - ", int(ID[4:10], 16)
        print "Checksum: ", Checksumme
        print "------------------------------------------"


        return card





