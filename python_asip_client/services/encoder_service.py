from services.asip_service import AsipService
import sys

class EncoderService(AsipService):
    DEBUG = False
    _serviceID = 'E'

    # An encoder has a unique ID (there may be more than one encoder attached, each one has a different encoderID)
    _encoderID = ""
    asip = None # The service should be attached to a client
    _count = 0 # Count for the encoder
    _pulse = 0 # Pulse for the encoder

    # Service constant
    __TAG_ENCODER_RESPONSE = 'e'

    # The constructor takes the id of the encoder sensor.
    def __init__(self, id, asipclient):
        AsipService.__init__(self)
        self._encoderID = id
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

    def get_encoder_id(self):
        return self._encoderID

    def set_encoder_id(self, id):
        self._encoderID = id

    # Set the reporting time to t milliseconds (use t=0 to disable reporting)
    # Notice that this will affect all encoders
    def set_reporting_interval(self, t):
        #self.asip.get_asip_writer().write(self._serviceID+","+AsipService.AUTOEVENT_REQUEST+","+t)
        self.asip.get_asip_writer().write("{},{},{}".format(self._serviceID,AsipService.AUTOEVENT_REQUEST,t))

    def process_response(self, message):
        # A response for a message is something like "@E,e,2,{3000:110,3100:120}"
        if message[3] != self.__TAG_ENCODER_RESPONSE:
            # FIXME: improve error checking
            # We have received a message but it is not an encoder reporting event
            sys.stdout.write("Distance message received but I don't know how to process it: {}\n".format(message))
        else:
            if self.DEBUG:
                sys.stdout.write("DEBUG: received message is {}\n".format(message))
            # enc_values = message[message.indexOf("{")+1: message.indexOf("}")].split(",")
            enc_values = message[message.index("{")+1: message.index("}")].split(",")
            self._pulse = int(enc_values[self._encoderID].split(':')[0])
            c = int(enc_values[self._encoderID].split(':')[1])
            self._count += c
            if self.DEBUG:
                sys.stdout.write("DEBUG: count and pulse to: {} {} {}\n".format(c,self._pulse,self._count))

    def get_count(self):
        return self._count

    def get_pulse(self):
        return self._pulse

    def reset_count(self):
        self._count= 0