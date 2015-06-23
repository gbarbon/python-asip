__author__ = 'Gianluca Barbon'

from mqtt_board import MQTTBoard
import sys
import time


# A simple board with just the I/O services on a fixed port.
# The main method simulates a light switch.
class MQTTMultipleThroughput(MQTTBoard):

    def __init__(self, broker, board):
        MQTTBoard.__init__(self, broker, board)
        self.input_pins = [2, 3, 4, 5, 6, 7]  # numbers of the pins that will be set in input mode
        self.ledPin = 13  # the number for the LED pin on the Arduino
        self.general_state = self.asip.LOW
        self.oldstate = self.asip.LOW
        self.pin_states = [self.asip.LOW] * 6

        self.init_conn()

    # init_conn initializes the pin
    def init_conn(self):
        try:
            time.sleep(0.5)
            self.asip.set_pin_mode(self.ledPin, self.asip.OUTPUT)
            for pin in self.input_pins:
                time.sleep(0.2)
                self.asip.set_pin_mode(pin, self.asip.INPUT)
        except Exception as e:
            sys.stdout.write("Exception caught while setting pin mode: {}\n".format(e))
            self.thread_killer()
            sys.exit(1)

    def main(self):
        while True:
            try:
                # check the value of the pin
                self.general_state = self.state()

                # check if the value is changed with respect to previous iteration
                if self.general_state != self.oldstate:
                    if self.general_state == self.asip.HIGH:
                        self.asip.digital_write(self.ledPin, self.asip.HIGH)
                    else:
                        self.asip.digital_write(self.ledPin, self.asip.LOW)
                self.oldstate = self.general_state
                time.sleep(0.001)  # Needed for thread scheduling/concurrency

            except (KeyboardInterrupt, Exception) as e:
                sys.stdout.write("Caught exception in main loop: {}\n".format(e))
                self.thread_killer()
                sys.exit()

    # This method retrieves the state of pins
    def state(self):
        big_pins = self.asip.get_digital_pins()
        self.pin_states = big_pins[2:7]
        if all(i == self.asip.LOW for i in self.pin_states):
            return self.asip.LOW
        elif all(i == self.asip.HIGH for i in self.pin_states):
            return self.asip.HIGH
        else:
            sys.stdout.write("Something wrong!\n")
            for i in self.input_pins:
                sys.stdout.write("Pin {} has value {}\n".format(i, self.pin_states[self.input_pins.index(i)]))
            return self.oldstate

if __name__ == "__main__":
    broker_ip = "169.254.83.106"
    board_id = "board4"
    MQTTMultipleThroughput(broker_ip, board_id).main()