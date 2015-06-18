__author__ = 'Gianluca Barbon'

from asip_client import AsipClient
from simple_mqtt_board import SimpleMQTTBoard
import sys
import time

# A simple board with just the I/O services on a fixed port.
#  The main method simulates a light switch.
class TwoBoardSwitch():

    def __init__(self, Broker):
        self.board2 = SimpleMQTTBoard(Broker, "board2")
        self.board4 = SimpleMQTTBoard(Broker, "board4")

        self.buttonPin = 2 # the number for the pushbutton pin on the Arduino
        self.ledPin = 13  # the number for the LED pin on the Arduino
        self.buttonState = 0 # initialise the variable for when we press the button

        # read the current state of the button
        # TODO: missing LOW and HIGH constants on AsipClient class
        # oldstate = AsipClient.LOW
        self.oldstate = 0

        #self.init_conn()

    # init_conn initializes the pin
    def init_conn(self):
        try:
            time.sleep(0.5)
             #stopping continuous analog output reporting
            self.board2.set_auto_report_interval(0)
            self.board4.set_auto_report_interval(0)
            time.sleep(0.5)
            self.board4.set_pin_mode(self.ledPin, AsipClient.OUTPUT)
            time.sleep(0.5)
            #self.set_pin_mode(self.buttonPin, AsipClient.INPUT_PULLUP)
            self.board2.set_pin_mode(self.buttonPin, AsipClient.INPUT_PULLUP)
        except Exception as e:
            sys.stdout.write("Exception: caught {} in setting pin mode\n".format(e))

    def main(self):
        while True:
            # check the value of the pin
            self.buttonState = self.board2.digital_read(self.buttonPin)

            # check if the value is changed with respect to previous iteration
            if self.buttonState != self.oldstate:
                if self.buttonState ==1:
                    self.board4.digital_write(self.ledPin, 1)
                else:
                    self.board4.digital_write(self.ledPin, 0)
            self.oldstate = self.buttonState

# test LightSwitch
if __name__ == "__main__":
    Broker = "192.168.0.101"
    TwoBoardSwitch(Broker)\
    #.main()
