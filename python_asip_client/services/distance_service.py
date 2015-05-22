from services.asip_service import AsipService
import sys

class DistanceService(AsipService):
    DEBUG = False
    _serviceID = 'D'

    # A distance sensor has a unique ID (there may be more than one distance sensor attached,
    # each one has a different distanceID)
    _distanceID = ""
    asip = None # The service should be attached to a client
    _last_distance = -1 # This is the last measured distance (-1 if not initialised)

    # Service constants
    __REQUEST_SINGLE_DISTANCE = 'M'
    __DISTANCE_EVENT = 'e'

    # The constructor takes the id of the distance sensor.
    def __init__(self, id, asipclient):
        AsipService.__init__(self)
        self._distanceID = id
        self.asip = asipclient

    # *** Standard getters and setters ***
    def get_service_id(self):
        return self._serviceID

    def set_service_id(self,id):
        self._serviceID = id

    def request_distance(self):
        #self.asip.get_asip_writer().write(self._serviceID+","+self.__REQUEST_SINGLE_DISTANCE+"\n")
        self.asip.get_asip_writer().write("{},{}".format(self._serviceID,self.__REQUEST_SINGLE_DISTANCE))

    def get_distance(self):
        return self._last_distance

    def enable_continuous_reporting(self,interval):
        #self.asip.get_asip_writer().write(self._serviceID+","+AsipService.AUTOEVENT_REQUEST+","+interval+"\n")
        self.asip.get_asip_writer().write("{},{},{}".format(self._serviceID,AsipService.AUTOEVENT_REQUEST,interval))

    def process_response(self, message):
        # A response for a message is something like "@D,e,1,25,35,..."
        if message[3] != self.__DISTANCE_EVENT:
            # FIXME: improve error checking
            # We have received a message but it is not a distance reporting event
            sys.stdout.write("Distance message received but I don't know how to process it: {}\n".format(message))
        else:
            if self.DEBUG:
                sys.stdout.write("DEBUG: received message is {}\n".format(message))
            distances = message[message.index("{")+1: message.index("}")].split(",")
            self._last_distance = int(distances[self._distanceID])