__author__ = 'Gianluca Barbon'

from asip_client import AsipClient
from simple_serial_board import SimpleSerialBoard
import sys
import time

# A simple board with just the I/O services on a fixed port.
#  The main method simulates a light switch.
class LightSwitch(SimpleSerialBoard):

    def __init__(self):
        SimpleSerialBoard.__init__(self)
        self.buttonPin = 2 # the number for the pushbutton pin on the Arduino
        self.ledPin = 13  # the number for the LED pin on the Arduino
        self.buttonState = 0 # initialise the variable for when we press the button

        # read the current state of the button
        # TODO: missing LOW and HIGH constants on AsipClient class
        # oldstate = AsipClient.LOW
        self.oldstate = 0

        self.init_conn()

    # init_conn initializes the pin
    def init_conn(self):
        try:
            time.sleep(0.5)
            self.set_auto_report_interval(0) #stooping continuous analog output reporting
            time.sleep(0.5)
            self.set_pin_mode(self.ledPin, AsipClient.OUTPUT)
            time.sleep(0.5)
            self.set_pin_mode(self.buttonPin, AsipClient.INPUT_PULLUP)
        except Exception as e:
            sys.stdout.write("Exception: caught {} in setting pin mode\n".format(e))

    def main(self):
        while True:
            # check the value of the pin
            self.buttonState = self.digital_read(self.buttonPin)

            # check if the value is changed with respect to previous iteration
            if self.buttonState != self.oldstate:
                if self.buttonState ==1:
                    self.digital_write(self.ledPin, 1)
                else:
                    self.digital_write(self.ledPin, 0)
            self.oldstate = self.buttonState

# test LightSwitch
if __name__ == "__main__":
    LightSwitch().main()