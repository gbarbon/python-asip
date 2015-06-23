__author__ = 'Gianluca Barbon'

from mqtt_board import MQTTBoard
import sys
import time


# A simple board with just the I/O services on a fixed port.
# The main method simulates a light switch.
class MQTTLatency(MQTTBoard):

    def __init__(self, broker, board):
        MQTTBoard.__init__(self, broker, board)
        self.buttonPin = 2  # the number for the pushbutton pin on the Arduino
        self.ledPin = 13  # the number for the LED pin on the Arduino
        self.buttonState = self.asip.LOW

        self.init_conn()

    # init_conn initializes the pin
    def init_conn(self):
        try:
            time.sleep(0.5)
            self.asip.set_pin_mode(self.ledPin, self.asip.OUTPUT)
            time.sleep(0.5)
            self.asip.set_pin_mode(self.buttonPin, self.asip.INPUT)
        except Exception as e:
            sys.stdout.write("Exception caught while setting pin mode: {}\n".format(e))
            self.thread_killer()
            sys.exit(1)

    def main(self):
        i = 0
        total = 0
        while i < 100:
            try:
                # setting up
                self.buttonState = self.asip.LOW
                self.asip.digital_write(self.ledPin, self.asip.LOW)

                # wait before entering the loop
                sys.stdout.write("Starting\n")
                time.sleep(0.5)

                # setting the pin to high
                self.asip.digital_write(self.ledPin, self.asip.HIGH)

                # read time
                #timer1 = time.clock()
                timer1 = time.time() * 1000
                while self.buttonState != self.asip.HIGH:
                    self.buttonState = self.asip.digital_read(self.buttonPin)
                    time.sleep(0.0001)

                # read result time
                # timer2 = time.clock()
                timer2 = time.time() * 1000
                diff = timer2 - timer1
                sys.stdout.write("Latency time is: {}\n".format(diff))

                #
                i += 1
                total += diff

            except (KeyboardInterrupt, Exception) as e:
                sys.stdout.write("Caught exception in main loop: {}\n".format(e))
                self.thread_killer()
                sys.exit()

        try:
            # total average
            avg = total/i
            sys.stdout.write("\nNumber of iterations: {}.\n\n*** Average latency is: {} ms ***\n\n".format(i, avg))
        except (KeyboardInterrupt, Exception) as e:
                sys.stdout.write("Caught exception while computing average: {}\n".format(e))
        finally:
            self.thread_killer()
            sys.exit(0)

if __name__ == "__main__":
    broker_ip = "127.0.0.1"
    board_id = "board4"
    MQTTLatency(broker_ip, board_id).main()