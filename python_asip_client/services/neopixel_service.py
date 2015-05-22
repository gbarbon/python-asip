from services.asip_service import AsipService
import sys

class NeoPixelService(AsipService):
    DEBUG = False
    _serviceID = 'N'

    # A strip has a unique ID (there may be more than one strip attached, each one has a different stripID)
    _stripID = ""
    asip = None # The service should be attached to a client

    # Service constants
    __TAG_SET_STRIP_BRIGHTNESS = 'B'
    __TAG_SET_STRIP_COLOR = 'C'
    __TAG_SHOW_STRIP = 'S'

    # The constructor takes the id of the distance sensor.
    def __init__(self, id, asipclient):
        AsipService.__init__(self)
        self._stripID = id
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

    def get_strip_id(self):
        return self._stripID

    def set_strip_id(self, id):
        self._stripID = id

    def process_response(self, message):
        # No response from the strip
        pass

    def set_pixel_color(self, pixel, red, green, blue):
        if self.DEBUG:
            sys.stdout.write("DEBUG: setting colors on strip {} pixel {} to {} {} {}\n"
                             .format(self._stripID, pixel, red, green, blue))
        # self.asip.get_asip_writer().write(self._serviceID + ","
        #                                     + self.__TAG_SET_STRIP_COLOR + ","
        #                                     + self._stripID + ","
        #                                     + pixel + ","
        #                                     + red + "," + green + "," + blue)
        self.asip.get_asip_writer().write("{},{},{},{},{},{},{}".format(
            self._serviceID, self.__TAG_SET_STRIP_COLOR, self._stripID, pixel, red, green, blue))


    def set_brightness(self, b):
        if self.DEBUG:
            sys.stdout.write("DEBUG: setting brightness on strip {} to {}\n".format(self._stripID, b))
        # self.asip.get_asip_writer().write(self._serviceID + ","
        #                                     + self.__TAG_SET_STRIP_BRIGHTNESS + ","
        #                                     + self._stripID + ","
        #                                     + b)
        self.asip.get_asip_writer().write("{},{},{},{}".format(
            self._serviceID, self.__TAG_SET_STRIP_BRIGHTNESS, self._stripID, b))

    def show(self):
        if self.DEBUG:
            sys.stdout.write("DEBUG: show strip {}\n".format(self._stripID))
        # self.asip.get_asip_writer().write(self._serviceID + ","
        #                                     + self.__TAG_SHOW_STRIP + ","
        #                                     + self._stripID)
        self.asip.get_asip_writer().write("{},{},{}".format(
            self._serviceID, self.__TAG_SHOW_STRIP, self._stripID))