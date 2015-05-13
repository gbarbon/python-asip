__author__ = 'Gianluca Barbon'

from asip_client import AsipClient
from simple_serial_board import SimpleSerialBoard
import sys
import time
import os # for kbhit
from kbhit import KBHit


# A simple board with just the I/O services.
# The main method does a standard blink test.
class SimpleBlink(SimpleSerialBoard):

    __DEBUG = False

    def main(self):
        if os.name == 'nt':
            kb = KBHit()  # needed for windows to handle keyboard interrupt
            sys.stdout.write('Hit ESC to exit\n')
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
            if os.name == 'nt':
                if kb.kbhit():
                    c = kb.getch()
                    if ord(c) == 27: # ESC
                        kb.set_normal_term()
                        break
            try:
                self.digital_write(13, 1)
                time.sleep(1.25)
                self.digital_write(13, 0)
                time.sleep(1.25)
            except Exception as e:
                sys.stdout.write("Exception: caught {} in digital_write".format(e))


# test SimpleBlink
SimpleBlink().main()
sys.stdout.write("Quitting!\n")
os._exit(0)  