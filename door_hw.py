
import RPi.GPIO as GPIO
from time import sleep


# use the broadcom model for gpio pins
#
GPIO.setmode(GPIO.BCM)

RED_PIN = 16
GREEN_PIN = None
DOOR_PIN = 21
BEEP_PIN = None


pins = [RED_PIN, GREEN_PIN, DOOR_PIN, DOOR_PIN]




for pin in pins :
    if not pin :
        continue
    GPIO.setup(pin, GPIO.OUT)

    # turn pin off
    GPIO.output(pin, False)



def beep(on=True) :
    "Beeper on or off"

    if BEEP_PIN :
        GPIO.output(BEEP_PIN, on)




def red(on=True) :
    "Turn the red LED on or off"

    if RED_PIN :
        GPIO.output(RED_PIN, on)



def green(on=True) :
    "Turn the green LED on or off"


    if GREEN_PIN :
        GPIO.output(GREEN_PIN, on)





def latch(open=False) :
    "Open the latch when True"

    if DOOR_PIN :
        GPIO.output(DOOR_PIN, open)
    if open :
        print 'OPEN'
    else :
        print 'CLOSE'



def blink_red(blinks=3, on_time=.3, off_time=.2) :
    "blink the red LED, usually for an error"

    red(True)
    sleep(on_time)
    for x in range(1,blinks) :
        red(False)
        sleep(off_time)
        red(True)
        sleep(on_time)
    red(False)




def open_sesame(latch_time = 4) :
    "open the latch for time with green indicator"

    green(True)
    latch(True)
    sleep(latch_time)
    green(False)
    latch(False)
    



def test() :

    red()
    green()
    latch()

    t = False
    latch(True)
    for i in range(5) :
        red(t)
        t = not t
        green(t)
        sleep(.6)
    latch()
    red(False)
    green(False)

        


if __name__ == '__main__':
    test()
