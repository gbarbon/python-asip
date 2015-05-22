from services.asip_service import AsipService
import sys

class MotorService(AsipService):
    DEBUG = False
    _serviceID = 'M'

    # A motor has a unique ID (there may be more than one motor attached, each one has a different motorID)
    _motorID = ""
    asip = None # The service should be attached to a client

    # Service constant
    __TAG_SET_MOTOR_SPEED = 'm'

    # The constructor takes the id of the motor.
    def __init__(self, id, asipclient):
        AsipService.__init__(self)
        self._motorID = id
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

    def get_motor_id(self):
        return self._motorID

    def set_motor_id(self, id):
        self._motorID = id

    def process_response(self, message):
        # Do nothing for motors
        pass

    def set_motor(self, speed):
        # Speed should be between -100 and +100
        if speed > 255:
            speed = 255
        if speed < -255:
            speed = -255
        if self.DEBUG:
            sys.stdout.write("DEBUG: setting motor {} to {}\n".format(self._motorID,speed))

        # Motors have been mounted the other way around, so swapping IDs 0 with 1 for id
        # self.asip.get_asip_writer().write(self._serviceID + ","
        #                                     + self.__TAG_SET_MOTOR_SPEED + ","
        #                                     + str(0 if self._motorID == 1 else 1)  # swapping
        #                                     + "," + speed)
        self.asip.get_asip_writer().write("{},{},{},{}".format(
            self._serviceID, self.__TAG_SET_MOTOR_SPEED, 0 if self._motorID == 1 else 1, speed))

    # Stop the motor (just set speed to 0)
    def stop_motor(self):
        self.set_motor(0)