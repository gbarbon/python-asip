__author__ = 'Gianluca Barbon'

from services.asip_service import AsipService
from asip_client import AsipClient
import sys

class SparkfunWSService(AsipService):
    serviceID = 'P'

    DEBUG = False

    # A distance sensor has a unique ID (there may be more than one distance
    # sensor attached, each one has a different distanceID)
    _pressureID = 0

    # The service should be attached to a client
    asip = None

    # This is the last measured distance (-1 if not initialised)
    _lastPressure = -1

    # Some constants (see docs)
    REQUEST_SINGLE_PRESSURE = 'M';
    PRESSURE_EVENT = 'e';

    # The constructor takes the id of the distance sensor.
    def __init__(self, id, asipclient):
        AsipService.__init__(self)
        self.pressureID = id
        self.asip = asipclient
        self._lastPressure = -1

    def get_service_id(self):
        return self.serviceID

    def set_service_id(self,id):
        self.serviceID = id

    def request_pressure(self):
        self.asip.get_asip_writer().write(self.serviceID+","+self.REQUEST_SINGLE_PRESSURE+"\n")

    def enable_continuous_reporting(self,interval):
        self.asip.get_asip_writer().write(self.serviceID+","+AsipService.AUTOEVENT_REQUEST+","+interval+"\n")

    def get_pressure(self):
        return self._lastPressure

    def process_response(self, message):
        # A response for a message is something like "@D,e,1,25,35,..."
        if message[3] != self.PRESSURE_EVENT:
            # FIXME: improve error checking
            # We have received a message but it is not a distance reporting event
            sys.stdout.write("Distance message received but I don't know how to process it: {}".format(message))
        else:
            pressures = message[message.index("{")+1: message.index("}")]
            self._lastPressure = int(pressures.split(".")[self._pressureID])
            if self.DEBUG:
                sys.stdout.write("DEBUG: received message is {}\n".format(message))