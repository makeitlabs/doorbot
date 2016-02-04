import RPi.GPIO as GPIO
from time import sleep

class DoorHW:

    def __init__(self, red_pin=None, green_pin=None, door_pin=None, beep_pin=None):
        # use the broadcom model for gpio pins
        #
        GPIO.setmode(GPIO.BCM)

        self.RED_PIN = red_pin
        self.GREEN_PIN = green_pin
        self.DOOR_PIN = door_pin
        self.BEEP_PIN = beep_pin

        self.pins = [self.RED_PIN, self.GREEN_PIN, self.DOOR_PIN, self.DOOR_PIN]

        for pin in self.pins :
            if not pin :
                continue
            GPIO.setup(pin, GPIO.OUT)

            # turn pin off
            GPIO.output(pin, False)

    def __del__(self):
        GPIO.cleanup()

    def beep(self, on=True):
        "Beeper on or off"

        if self.BEEP_PIN:
            GPIO.output(self.BEEP_PIN, on)

    def red(self, on=True):
        "Turn the red LED on or off"

        if self.RED_PIN:
            GPIO.output(self.RED_PIN, not on)

    def green(self, on=True):
        "Turn the green LED on or off"

        if self.GREEN_PIN:
            GPIO.output(self.GREEN_PIN, not on)

    def latch(self, open=False):
        "Open the latch when True"

        if self.DOOR_PIN:
            GPIO.output(self.DOOR_PIN, open)
        if open :
            print('OPEN')
        else :
            print('CLOSE')

    def blink_red(self, blinks=3, on_time=.3, off_time=.2):
        "blink the red LED, usually for an error"

        self.red(True)
        sleep(on_time)
        for x in range(1,blinks) :
            self.red(False)
            sleep(off_time)
            self.red(True)
            sleep(on_time)
        self.red(False)

    def open_sesame(self, latch_time=4):
        "open the latch for time with green indicator"
        self.green(True)
        self.latch(True)
        sleep(latch_time)
        self.green(False)
        self.latch(False)

    def test(self):

        self.red()
        self.green()
        self.latch()

        t = False
        self.latch(True)
        for i in range(5) :
            self.red(t)
            t = not t
            self.green(t)
            sleep(.6)
        self.latch()
        self.red(False)
        self.green(False)

        
if __name__ == '__main__':
    test()

    
