__author__ = 'Gianluca Barbon'

from asip_client import AsipClient
from simple_tcp_board import SimpleTCPBoard
import sys
import time


# A simple board with just the I/O services.
# The main method does a standard blink test.
class SimpleBlink(SimpleTCPBoard):

    __DEBUG = True

    def main(self):
        try:
            #time.sleep(1)
            #self.request_port_mapping()
            time.sleep(0.5)
            self.set_pin_mode(13, AsipClient.OUTPUT)
            time.sleep(0.5)
            self.set_pin_mode(2, AsipClient.INPUT_PULLUP)
            time.sleep(0.5)
        except Exception as e:
            sys.stdout.write("Exception: caught {} in setting pin mode".format(e))

        while True:
            try:
                self.digital_write(13, 1)
                time.sleep(0.25)
                self.digital_write(13, 0)
                time.sleep(0.25)
            except Exception as e:
                sys.stdout.write("Exception: caught {} in digital_write".format(e))


# test SimpleBlink
#IPaddress = "192.168.0.102"
IPaddress = "127.0.0.1"
SimpleBlink(IPaddress).main()