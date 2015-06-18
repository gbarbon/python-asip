__author__ = 'Gianluca Barbon'

from serial_board import SerialBoard
import sys
import time
import os # for kbhit
from kbhit import KBHit


# A simple board with just the I/O services.
# The main method does a standard blink test.
class SimpleBlink(SerialBoard):

    def main(self):
        if os.name == 'nt':
            kb = KBHit()  # needed for windows to handle keyboard interrupt
            sys.stdout.write('Hit ESC to exit\n')
        try:
            time.sleep(0.5)
            self.asip.set_pin_mode(13, self.asip.OUTPUT)
            time.sleep(0.5)
        except Exception as e:
            sys.stdout.write("Exception caught while setting pin mode: {}\n".format(e))
            self.thread_killer()
            sys.exit(1)

        while True:        
            if os.name == 'nt':
                if kb.kbhit():
                    c = kb.getch()
                    if ord(c) == 27:  # ESC
                        kb.set_normal_term()
                        break
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
    SimpleBlink().main()
sys.stdout.write("Quitting!\n")
#os._exit(0)
sys.exit(0)