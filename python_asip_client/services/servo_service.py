from services.asip_service import AsipService
import sys

class ServoService(AsipService):
    DEBUG = False
    _serviceID = 'S'

    # A servo has a unique ID (there may be more than one servo attached, each one has a different servoID)
    _servoID = ""
    asip = None # The service should be attached to a client

    # Service constant
    __TAG_SET_SERVO_ANGLE = 'W'

    # The constructor takes the id of the servo motor.
    def __init__(self, id, asipclient):
        AsipService.__init__(self)
        self._servoID = id
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

    def get_servo_id(self):
        return self._servoID

    def set_servo_id(self, id):
        self._servoID = id

    def process_response(self, message):
        # No response from the servo
        pass

    def set_servo(self, angle):
        if self.DEBUG:
            sys.stdout.write("DEBUG: setting servo {} to {}\n".format(self._servoID,angle))
        # self.asip.get_asip_writer().write(self._serviceID + ","
        #                                     + self.__TAG_SET_SERVO_ANGLE + ","
        #                                     + self._servoID + ","
        #                                     + angle)
        self.asip.get_asip_writer().write("{},{},{},{}".format(
            self._serviceID, self.__TAG_SET_SERVO_ANGLE, self._servoID, angle))