__author__ = 'Gianluca Barbon'

from asip_client import AsipClient
from simple_serial_board import SimpleSerialBoard
from port_manager import PortManager
import time

class SimpleBlink(SimpleSerialBoard):

    __DEBUG = True

    #def __init__(self, port):
    #    super(port)

    def main(self, args):
        # We could pass the port as an argument, for the moment
        # I hard-code it because I'm lazy.

        testBoard = SimpleBlink("/dev/cu.usbmodemfd121")

        #try:
        time.sleep(1)
        testBoard.request_port_mapping()
        time.sleep(0.5)
        testBoard.set_pin_mode(13, AsipClient.OUTPUT)
        time.sleep(0.5)
        testBoard.set_pin_mode(2, AsipClient.INPUT_PULLUP)
        time.sleep(0.5)
        #except Exception as e:
        #    print("Exception in setting pin mode")

        while True:
            #try:
            testBoard.digital_write(13, 1)
            time.sleep(0.25)
            testBoard.digital_write(13, 0)
            time.sleep(0.25)
            #except Exception as e:
                #print("Exception is port manager")

SimpleBlink("/dev/cu.usbmodemfd121").main(None)