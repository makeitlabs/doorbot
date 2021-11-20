sudo avrdude -p atmega328p -C avrdude.conf -c pi_1 -v -U flash:w:WiegandTest.ino.eightanaloginputs.hex
