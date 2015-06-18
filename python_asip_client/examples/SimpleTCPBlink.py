__author__ = 'Gianluca Barbon'

from tcp_board import TCPBoard
import sys
import time


# A simple board with just the I/O services.
# The main method does a standard blink test.
class SimpleTCPBlink(TCPBoard):

    def main(self):
        try:
            time.sleep(0.5)
            self.asip.set_pin_mode(13, self.asip.OUTPUT)
            time.sleep(0.5)
        except Exception as e:
            sys.stdout.write("Exception caught while setting pin mode: {}\n".format(e))
            self.thread_killer()
            sys.exit(1)

        while True:
            try:
                self.asip.digital_write(13, self.asip.HIGH)
                time.sleep(1.25)
                self.asip.digital_write(13, self.asip.LOW)
                time.sleep(1.25)
            except (KeyboardInterrupt, Exception) as e:
                sys.stdout.write("Caught exception in main loop: {}\n".format(e))
                self.thread_killer()
                sys.exit()


# test SimpleBlink
if __name__ == "__main__":
    IPaddress = "192.168.0.100"
    SimpleTCPBlink(IPaddress).main()