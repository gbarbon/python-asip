__author__ = 'Gianluca barbon'

from serial_board import SerialBoard
import sys
import time


# this class provides a simple example of how it is possible to read analog values into the Arduino
# in this case, the readings we get control the rate at which the LED blinks.
class Potentiometer(SerialBoard):

    def __init__(self):
        SerialBoard.__init__(self)
        self.potPin = 2  # the number for the potentiometer pin on the Arduino
        self.ledPin = 13  # the number for the LED pin on the Arduino
        self.potValue = 0  # initialise the variable storing the potentiometer readings
        self.init_conn()

    # init_conn initializes the pins
    def init_conn(self):
        try:
            time.sleep(0.1)
            self.asip.set_auto_report_interval(50)
            time.sleep(0.1)  # then stop the program for some time
            self.asip.set_pin_mode(self.ledPin, self.asip.OUTPUT)  # declare the LED pin as an output
            time.sleep(0.1)
            self.asip.set_pin_mode(self.potPin+14, self.asip.ANALOG)
            time.sleep(0.1)
        except Exception as e:
            sys.stdout.write("Exception caught while setting pin mode: {}\n".format(e))
            self.thread_killer()
            sys.exit(1)

    def main(self):
        # Set the LED to blink with a delay  based on the current value of the potentiometer
        while True:
            try:
                self.potValue = self.asip.analog_read(self.potPin)  # read the potentiometer
                self.asip.digital_write(self.ledPin, self.asip.HIGH)  # turn the LED pin on
                time.sleep(0.2+self.potValue*0.001)  # then stop the program for some time
                self.asip.digital_write(self.ledPin, self.asip.LOW)  # turn the LED pin off
                time.sleep(0.2+self.potValue*0.001)  # then stop the program for some time
            except (KeyboardInterrupt, Exception) as e:
                sys.stdout.write("Caught exception in main loop: {}\n".format(e))
                self.thread_killer()
                sys.exit()

# test Potentiometer
if __name__ == "__main__":
    Potentiometer().main()