__author__ = 'Gianluca barbon'

from asip_client import AsipClient
from simple_serial_board import SimpleSerialBoard
import sys
import time


# this class provides a simple example of how it is possible to read analog values into the Arduino
# in this case, the readings we get control the rate at which the LED blinks.
class Potentiometer(SimpleSerialBoard):

    def __init__(self):
        SimpleSerialBoard.__init__(self)
        self.potPin = 2 # the number for the potentiometer pin on the Arduino
        self.ledPin = 13  # the number for the LED pin on the Arduino
        self.potValue = 0 # initialise the variable storing the potentiometer readings
        self.init_conn()

    # init_conn initializes the pin
    def init_conn(self):
        try:
            #self.request_port_mapping()
            time.sleep(0.1)
            self.set_auto_report_interval(50)
            time.sleep(0.1)					# then stop the program for some time
            self.set_pin_mode(self.ledPin, AsipClient.OUTPUT)  # declare the LED pin as an output
            time.sleep(0.1)
            self.set_pin_mode(self.potPin+14, AsipClient.ANALOG)
            time.sleep(0.1)
        except Exception as e:
            sys.stdout.write("Exception: caught {} in setting pin mode\n".format(e))

    def main(self):
        # Set the LED to blink with a delay  based on the current value of the potentiometer
        while True :
            self.potValue = self.analog_read(self.potPin) # read the potentiometer
            self.digital_write(self.ledPin, 1)	 	 # turn the LED pin on
            try:
                time.sleep(0.2+self.potValue*0.001) 							# then stop the program for some time
            except Exception as e:
                sys.stdout.write("Exception: caught {} in first sleep\n".format(e))
            self.digital_write(self.ledPin, 0)   	# turn the LED pin off
            try:
                time.sleep(0.2+self.potValue*0.001)						# then stop the program for some time
            except Exception as e:
                sys.stdout.write("Exception: caught {} in second sleep\n".format(e))

# test Potentiometer
if __name__ == "__main__":
    Potentiometer().main()