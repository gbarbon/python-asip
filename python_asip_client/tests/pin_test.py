__author__ = 'Gianluca Barbon'

from asip_client import AsipClient
from simple_serial_board import SimpleSerialBoard
import sys
import time

# A simple board to test pin connetions
class PinTest(SimpleSerialBoard):

    def __init__(self):
        SimpleSerialBoard.__init__(self)
        self.button_pin = 0 # the number for the pushbutton pin on the Arduino
        self.led_pin = 0  # the number for the LED pin on the Arduino
        self.buttonState = 0 # initialise the variable for when we press the button

        self.pinset = [[7,2],[8,13]]

        self.oldstate = 0

    # init_conn initializes the pin
    def set_pin(self, couple):
        try:
            self.button_pin = couple[0]
            self.led_pin = couple[1]
            time.sleep(0.5)
            self.set_auto_report_interval(0) #stooping continuous analog output reporting
            time.sleep(0.5)
            self.set_pin_mode(self.led_pin, AsipClient.OUTPUT)
            time.sleep(0.5)
            self.set_pin_mode(self.button_pin, AsipClient.INPUT_PULLUP)
        except Exception as e:
            sys.stdout.write("Exception: caught {} in setting pin mode\n".format(e))

    def main(self):
        self.set_pin(self.pinset[0])
        print(self.button_pin, self.led_pin)
        while True:
            # check the value of the pin
            self.buttonState = self.digital_read(self.button_pin)

            # check if the value is changed with respect to previous iteration
            if self.buttonState != self.oldstate:
                if self.buttonState ==1:
                    self.digital_write(self.led_pin, 1)
                else:
                    self.digital_write(self.led_pin, 0)
            self.oldstate = self.buttonState

# test LightSwitch
if __name__ == "__main__":
    PinTest().main()