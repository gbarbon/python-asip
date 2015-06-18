__author__ = 'Gianluca Barbon'

from tcp_board import TCPBoard
import sys
import time


# A simple board with just the I/O services on a fixed port.
#  The main method simulates a light switch.
class LightSwitchTCP(TCPBoard):

    def __init__(self, IP):
        TCPBoard.__init__(self, IP)
        self.buttonPin = 2  # the number for the pushbutton pin on the Arduino
        self.ledPin = 13  # the number for the LED pin on the Arduino
        self.buttonState = self.asip.LOW
        self.oldstate = self.asip.LOW

        self.init_conn()

    # init_conn initializes the pin
    def init_conn(self):
        try:
            time.sleep(0.5)
            self.asip.set_pin_mode(self.ledPin, self.asip.OUTPUT)
            time.sleep(0.5)
            self.asip.set_pin_mode(self.buttonPin, self.asip.INPUT_PULLUP)
        except Exception as e:
            sys.stdout.write("Exception caught while setting pin mode: {}\n".format(e))
            self.thread_killer()
            sys.exit(1)

    def main(self):
        while True:
            try:
                # check the value of the pin
                self.buttonState = self.asip.digital_read(self.buttonPin)

                # check if the value is changed with respect to previous iteration
                if self.buttonState != self.oldstate:
                    if self.buttonState == 1:
                        self.asip.digital_write(self.ledPin, self.asip.HIGH)
                    else:
                        self.asip.digital_write(self.ledPin, self.asip.LOW)
                self.oldstate = self.buttonState

                time.sleep(0.005)  # Needed for thread scheduling/concurrency

            except (KeyboardInterrupt, Exception) as e:
                sys.stdout.write("Caught exception in main loop: {}\n".format(e))
                self.thread_killer()
                sys.exit()

# test LightSwitch
if __name__ == "__main__":
    IP = "192.168.0.100"
    LightSwitchTCP(IP).main()