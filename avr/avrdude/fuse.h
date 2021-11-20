sudo avrdude -p atmega328p -C avrdude.conf -c pi_1 -v -U lfuse:w:0xff:m -U hfuse:w:0xda:m -U efuse:w:0xfd:m

