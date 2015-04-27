__author__ = 'Gianluca Barbon'

from asip_client import AsipClient
from simple_serial_board import SimpleSerialBoard
from services import sparkfunws_service
import sys
import time


# A simple board with just the I/O services.
# The main method does a standard blink test.
class SimplePressure(SimpleSerialBoard):

    p0 = None

    __DEBUG = False

    def __init__(self):
        SimpleSerialBoard.__init__(self)
        try:
            time.sleep(0.3)
            self.p0 = sparkfunws_service.SparkfunWSService(0, self.get_asip_client())
            time.sleep(0.3)
            self.get_asip_client().set_auto_report_interval(0)
        except Exception as e:
            sys.stdout.write("Exception: caught {} in init\n".format(e))
        try:
            self.add_service('P', self.p0)
            time.sleep(0.3)
        except Exception as e:
            sys.stdout.write("Exception 2: caught {} in init\n".format(e))

        try:
            self.p0.enable_continuous_reporting('500')
            time.sleep(0.1)
            self.get_asip_client().set_auto_report_interval('0')
        except Exception as e:
            sys.stdout.write("Exception 3: caught {} in init\n".format(e))

    def get_pressure(self):
        return self.p0.get_pressure()

    def main(self):

        while True:
            try:
                time.sleep(0.5)
                sys.stdout.write("Pressure is {}\n".format(self.get_pressure()))
            except Exception as e:
                sys.stdout.write("Exception: caught {} in digital_write".format(e))


# test SimpleBlink
SimplePressure().main()
