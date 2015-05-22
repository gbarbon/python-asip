from services.asip_service import AsipService
import sys

class IRService(AsipService):
    DEBUG = False
    _serviceID = 'R'

    # An ir sensor has a unique ID (there may be more than one ir sensor attached, each one has a different irID)
    _irID = ""
    asip = None # The service should be attached to a client
    _value = 0 # value for the sensor

    # Service constant
    __TAG_IR_RESPONSE = 'e'

    # The constructor takes the id of the ir sensor.
    def __init__(self, id, asipclient):
        AsipService.__init__(self)
        self._irID = id
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

    def get_ir_id(self):
        return self._irID

    def set_ir_id(self, id):
        self._irID = id

    # Set the reporting time to t milliseconds (use t=0 to disable reporting)
    # Notice that this will affect all IR sensors
    def set_reporting_interval(self, t):
        #self.asip.get_asip_writer().write(self._serviceID+","+AsipService.AUTOEVENT_REQUEST+","+t)
        self.asip.get_asip_writer().write("{},{},{}".format(self._serviceID,AsipService.AUTOEVENT_REQUEST,t))

    def process_response(self, message):
        # A response for a message is something like "@R,e,3,{100,200,300}"
        if message[3] != self.__TAG_IR_RESPONSE:
            # FIXME: improve error checking
            # We have received a message but it is not a bump reporting event
            sys.stdout.write("Distance message received but I don't know how to process it: {}\n".format(message))
        else:
            if self.DEBUG:
                sys.stdout.write("DEBUG: received message is {}\n".format(message))
            ir_values = message[message.index("{")+1: message.index("}")].split(",")
            self._value = int(ir_values[self._irID])

    def get_ir(self):
        return self._value