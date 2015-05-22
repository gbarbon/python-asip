from services.asip_service import AsipService
import sys

class BumpService(AsipService):
    DEBUG = False
    _serviceID = 'B'

    # A bump sensor has a unique ID (there may be more than one bump sensor attached, each one has a different bumpID)
    _bumpID = ""
    asip = None # The service should be attached to a client
    _pressed = None # value for the sensor

    # Service constant
    __TAG_BUMP_RESPONSE = 'e'

    # The constructor takes the id of the bump sensor.
    def __init__(self, id, asipclient):
        AsipService.__init__(self)
        self._bumpID = id
        self.asip = asipclient

    # *** Standard getters and setters ***

    def get_service_id(self):
        return self._serviceID

    def set_service_id(self,id):
        self._serviceID = id

    # receives an instance of AsipClient as parameter
    def set_client(self, client):
        self.asip = client

    def get_client(self):
        return self.asip

    def get_bump_id(self):
        return self._bumpID

    def set_bump_id(self, id):
        self._bumpID = id

    # Set the reporting time to t milliseconds (use t=0 to disable reporting)
    # Notice that this will affect all bump sensors
    def set_reporting_interval(self, t):
        #self.asip.get_asip_writer().write(self._serviceID+","+AsipService.AUTOEVENT_REQUEST+","+t)
        self.asip.get_asip_writer().write("{},{},{}".format(self._serviceID,AsipService.AUTOEVENT_REQUEST,t))

    def process_response(self, message):
        # A response for a message is something like "@B,e,2,{0,1}"
        if message[3] != self.__TAG_BUMP_RESPONSE:
            # FIXME: improve error checking
            # We have received a message but it is not a bump reporting event
            sys.stdout.write("Distance message received but I don't know how to process it: {}\n".format(message))
        else:
            if self.DEBUG:
                sys.stdout.write("DEBUG: BUMP received message is {}\n".format(message))
            bump_values = message[message.index("{")+1: message.index("}")].split(",")
            self._pressed = False if int(bump_values[self._bumpID]) == 1 else True
            # in java is equivalent to ( (Integer.parseInt(bump_values[self._bumpID]) == 1) ? False : True)

    def is_pressed(self):
        return self._pressed