__author__ = 'Gianluca Barbon'

from asip_client import AsipClient
from simple_mqtt_board import SimpleMQTTBoard
import sys
import time
import os # for kbhit
from kbhit import KBHit


# A simple board with just the I/O services.
# The main method does a standard blink test.
class MQTTWaveTester(SimpleMQTTBoard):

    def __init__(self, Broker, BoardID):
        SimpleMQTTBoard.__init__(self, Broker, BoardID)
        self.buttonPin = 2 # the number for the pushbutton pin on the Arduino
        self.ledPin = 7  # the number for the LED pin on the Arduino
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
            self.set_pin_mode(self.buttonPin, AsipClient.INPUT)
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
            #else:
                #print("I'm here")
            self.oldstate = self.buttonState

if __name__ == "__main__":
    Broker = "192.168.0.100"
    BoardID = "test"
    MQTTWaveTester(Broker, BoardID).main()
    sys.stdout.write("Quitting!\n")
    os._exit(0)
