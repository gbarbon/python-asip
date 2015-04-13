__author__ = 'Gianluca Barbon'

# import AsipWriter
import sys
# import traceback


class AsipClient:

    # Constants inherited from Java client version
    # TODO: implement emulation of constant through dedicated file / function

    # ************   BEGIN CONSTANTS DEFINITION ****************
    DEBUG = False  # Do you want me to print verbose debug information?

    MAX_NUM_DIGITAL_PINS = 72  # 9 ports of 8 pins at most?
    MAX_NUM_ANALOG_PINS = 16  # Just a random number...

    # Low-level tags for I/O service:
    IO_SERVICE = 'I'  # tag indicating message is for I/O service
    PIN_MODE = 'P'  # i/o request  to Arduino to set pin mode
    DIGITAL_WRITE = 'd'  # i/o request  to Arduino is digitalWrite
    ANALOG_WRITE = 'a'  # i/o request to Arduino is analogWrite
    ANALOG_DATA_REQUEST = 'A'  # i/o request to Arduino to set Autoreport to a certain value in ms
    PORT_DATA = 'd'  # i/o event from Arduino is digital port data
    ANALOG_VALUE = 'a'  # i/o event from Arduino is value of analog pin
    PORT_MAPPING = 'M'  # i/o event from Arduino is port mapping to pins
    GET_PIN_MODES = 'p'  # gets a list of pin modes
    GET_PIN_SERVICES_LIST = 's'  # gets a list of pins indicating registered service
    # tag_GET_SERVICES_NAMES    = 'n' # gets a list of service tags/name pairs
    GET_PIN_CAPABILITIES = 'c'  # gets a bitfield array indicating pin capabilities

    # Pin modes (these are public)
    INPUT = 1  # defined in Arduino.h
    INPUT_PULLUP = 2  # defined in Arduino.h
    OUTPUT = 3  # defined in Arduino.h
    ANALOG = 4  # analog pin in analogInput mode
    PWM = 5  # digital pin in PWM output mode

    EVENT_HANDLER = '@'  # Standard incoming message
    ERROR_MESSAGE_HEADER = '~'  # Incoming message: error report
    DEBUG_MESSAGE_HEADER = '!'  # A debug message from the board (can be ignored, probably)

    HIGH = 1
    LOW = 0
    # ************   END CONSTANTS DEFINITION ****************

    # ************   BEGIN PRIVATE FIELDS DEFINITION ****************
    __digital_input_pins = []
    __analog_input_pins = []
    __pin_mode = []  # FIXME: do we need this at all?

    # TODO: define hash map
    # We need to store that port x at position y corresponds to PIN z.
    # We store this as a map from port numbers (x) to another map
    # position(y)->pin(z).
    # (see below the description of processPinMapping())
    # private HashMap<Integer,HashMap<Integer,Integer>> __port_mapping;
    # use of the dict for python for hashmap
    __port_mapping = {}

    # A map from service IDs to actual implementations.
    # FIXME: there could be more than one service with the same ID!
    # (two servos, two distance sensors, etc).
    # private HashMap<Character,LinkedList<AsipService>> services;
    # use of the dict for python for hashmap
    __services = {}

    # The output channel (where we write messages). This should typically be a serial port, but could be anything else.
    # out = AsipWriter()
    __out = None

    # ************   END PRIVATE FIELDS DEFINITION ****************

    #  A constructor taking the writer as parameter.
    def __init__(self, w=None):

        # Ports, pins, and services initialization
        # port_mapping = new HashMap<Integer,HashMap<Integer,Integer>>();
        self.__port_mapping = None
        self.__digital_input_pins = [None]*self.MAX_NUM_DIGITAL_PINS
        self.__analog_input_pins = [None]*self.MAX_NUM_ANALOG_PINS
        self.__pin_mode = [None]*(self.MAX_NUM_DIGITAL_PINS + self.MAX_NUM_ANALOG_PINS)
        # services = new HashMap<Character,LinkedList<AsipService>>();
        self.__services = None

        if self.DEBUG:
            sys.stdout.write('End of constructor: arrays and maps created')
            pass

        # constructor also work without writer parameter
        if w is not None:
            self.__out = w

    # ************ BEGIN PUBLIC METHODS *************
    # This method processes an input received on the serial port.
    # See protocol description for more detailed information.
    def process_input(self, input_str):
        if input_str == self.EVENT_HANDLER:
            self.__handle_input_event(input_str)

        elif input_str == self.ERROR_MESSAGE_HEADER:
            self.__handle_input_error(input_str)

        elif input_str == self.DEBUG_MESSAGE_HEADER:
            self.__handle_input_event(input_str)

        else:
            # FIXME: better error handling required!
            if self.DEBUG:
                sys.stdout.write('Strange character received at position 0: ' + input_str)

    # A method to request the mapping between ports and pins, see
    # process_port_data and process_pin_mapping for additional details
    # on the actual mapping.
    def request_port_mapping(self):
        self.__out.write(self.IO_SERVICE+','+self.PORT_MAPPING+'\n')
        if self.DEBUG:
            sys.stdout.write('DEBUG: Requesting port mapping with ' + self.IO_SERVICE + ',' + self.PORT_MAPPING + '\n')

    def digital_read(self, pin):
        # FIXME: should add error checking here
        return self.__digital_input_pins[pin]

    def analog_read(self, pin):
        # FIXME: should add error checking here
        return self.__analog_input_pins[pin]

    def set_pin_mode(self, pin, mode):
        self.__out.write(self.IO_SERVICE + "," + self.PIN_MODE + "," + pin + "," + mode + "\n")
        if self.DEBUG:
            sys.stdout.write(
                "DEBUG: Setting pin mode with " + self.IO_SERVICE + "," + self.PIN_MODE + "," + pin + "," + mode)

    # A method to write to a digital pin
    def digital_write(self, pin, value):
        self.__out.write(self.IO_SERVICE + "," + self.DIGITAL_WRITE + "," + pin + "," + value + "\n")
        if self.DEBUG:
            sys.stdout.write(
                "DEBUG: Setting digital pin with " + self.IO_SERVICE + "," + self.DIGITAL_WRITE + "," + pin + "," + value)

    # A method to write to an analog pin
    def analog_write(self, pin, value):
        self.__out.write(self.IO_SERVICE + "," + self.ANALOG_WRITE + "," + pin + "," + value + "\n")
        if self.DEBUG:
            sys.stdout.write(
                "DEBUG: Setting analog pin with " + self.IO_SERVICE + "," + self.DIGITAL_WRITE + "," + pin + "," + value)

    # A method to set the autoreport interval (in ms)
    def set_auto_report_interval(self, interval):
        self.__out.write(self.IO_SERVICE + "," + self.ANALOG_DATA_REQUEST + "," + interval + "\n")
        if self.DEBUG:
            sys.stdout.write(
                "DEBUG: Setting autoreport interval " + self.IO_SERVICE + "," + self.ANALOG_DATA_REQUEST + "," + interval)

    # It is possible to add services at run-time:
    def add_service(self, service_id, asip_service):
        # If there is already a service with the same ID, we add this
        # new one to the list. Otherwise, we create a new entry.
        if service_id in self.__services:
            self.__services[service_id] = asip_service
        else:
            self.__services.update({service_id: asip_service})

    # TODO: fix code below, add a list of services instead of a single one
    # It is possible to add services at run-time (this one takes a list):
    # def addService(self, serviceID, LinkedList<AsipService> s) :
    #services.put(serviceID,s)
    # pass

    # Just return the list of services
    def get_services(self):
        return self.__services

    # I'm not sure we want this public... FIXME?
    def get_digital_pins(self):
        return self.__digital_input_pins

    # Getter and Setter for output channel
    def get_asip_writer(self):
        return self.__out

    def set_asip_writer(self, w):
        self.__out = w

    # ************ END PUBLIC METHODS *************

    #************ BEGIN PRIVATE METHODS *************

    # A method to do what is says on the tin...
    def __handle_input_event(self, input_str):
        if self.DEBUG:
            sys.stdout.write("DEBUG: received message "+input_str)

        if input_str[1] == self.IO_SERVICE:
            # Digital pins (in port)

            # the port data event is something like: @I,P,4,F
            # this message says the data on port 4 has a value of F

            if input_str[3] == self.PORT_DATA:
                # We need to process port number and bit mask for it
                port = int(input_str[5:6])
                bitmask = int(input_str[7:7], 16)  # convert to base 16
                self.__process_port_data(port, bitmask)
            elif input_str[3] == self.PORT_MAPPING:
                self.__process_pin_mapping(input_str)
            elif input_str[3] == self.ANALOG_VALUE:
                if self.DEBUG:
                    sys.stdout.write("DEBUG: received message " + input_str)

                    # This is a list of strings "pin1:value1","pin2:value2",...
                    try:
                        pin_values = input_str[input_str.index("{")+1:input_str.index("}")].split(",")
                        for pin_val in pin_values:
                            pin_id = int(pin_val.split(":")[0])
                            val = int(pin_val.split(":")[1])
                            self.__analog_input_pins[pin_id] = val
                            if self.DEBUG:
                                sys.stdout.write("DEBUG: setting analog pin " + str(pin_id) + " to " + str(val))
                    except Exception as e:
                        if self.DEBUG:
                            sys.stdout.write("DEBUG: exception while parsing analog message")
                            sys.stdout.write(e)
                            #traceback.print_exc()

            # TODO: implement missing messages!
            else:
                if self.DEBUG:
                    sys.stdout.write("Service not recognised in position 3 for I/O service: " + input_str)
        # end of IO_SERVICE

        elif input_str[1] in self.__services.keys():
            # Is this one of the services we know? If this is the case, we call it and we process the input
            # I want a map function here!! For the moment we use a for loop...
            for s in self.__services[input_str[1]]:
                s.processResponse(input_str)

        else:
            # We don't know what to do with it.
            if self.DEBUG:
                sys.stdout.write("Event not recognised at position 1: " + input_str)

    # To handle a message starting with an error header (this is a form of error reporting from Arduino)
    def __handle_input_error(self, input_str):
        # FIXME: improve error handling
        if self.DEBUG:
            sys.stdout.write("Error message received: "+input_str)

    # For the moment we just report board's debug messages on screen
    # FIXME: do something smarter?
    def __handle_debug_event(self, input_str):
        if self.DEBUG:
            sys.stdout.write("DEBUG: " + input_str)

    # A method to process input messages for digital pins.
    # We get a port and a sequence of bits. The mapping between ports and pins
    # is stored in port_mapping. See comments for processPinMapping for additional details.
    # FIXME: add the usual error checking etc. (Franco, you are too lazy!)
    def __process_port_data(self, port, bitmask):

        # FIXME: we should check that no data arrives before __port_mapping has been created initialized!
        if self.DEBUG:
            sys.stdout.write("DEBUG: processPortData for port " + port + " and bitmask " + bitmask)
        single_port_map = self.__port_mapping[port]

        for (key, value) in single_port_map.items():
            if (key & bitmask) != 0x0:
                self.__digital_input_pins[value] = self.HIGH
                if self.DEBUG:
                    sys.stdout.write("DEBUG: processPortData setting pin " + value + " to HIGH")
            else:
                self.__digital_input_pins[value] = self.LOW
                if self.DEBUG:
                    sys.stdout.write("DEBUG: processPortData setting pin " + value + " to LOW")

    # At the beginning we receive a mapping of the form:
    # @I,M,20{4:1,4:2,4:4,4:8,4:10,4:20,4:40,4:80,2:1,2:2,2:4,2:8,2:10,2:20,3:1,3:2,3:4,3:8,3:10,3:20}
    # This means that there are 20 PINs; PIN 0 is mapped in position 0 of port 4 (4:1)
    # PIN 1 is mapped in position 1 (2^1) of port 4;
    # PIN 2 is mapped in position 2 (2^2) of port 4, i.e. 4:4;
    # ...
    # PIN 4 is mapped in position 4 (2^4=16=0x10) of port 4, i.e. 4:10;
    # PIN 9 is mapped in position 2 of port 2, i.e. 2:2, etc.
    def __process_pin_mapping(self, mapping):
        # FIXME: maybe add a bit of error checking: check that the length corresponds to the number of PINs, etc.
        # For the moment I take the substring comprised between "{" and "}"
        # and I create an array of strings for each element.
        ports = mapping.substring[mapping.index("{")+1: mapping.index("}")].split(",")

        # I just iterate over the array getting each port:position
        cur_pin = 0
        for single_mapping in ports:
            port = int(single_mapping.split(":")[0])
            position = int(single_mapping.split(":")[1], 16)

            # If __port_mapping already contains something for this port,
            # we add the additional position mapping
            if port in self.__port_mapping:
                self.__port_mapping[port].update({position, cur_pin})
            else:
                # Otherwise, we create a new key in __port_mapping
                temp_dict = {position, cur_pin}
                self.__port_mapping.update(port, temp_dict)
            cur_pin += 1

        if self.DEBUG:
            sys.stdout.write("DEBUG: Port bits to PIN numbers mapping: ")
            sys.stdout.write("DEBUG: " + str(self.__port_mapping))

    # ************ END PRIVATE METHODS *************/

    # ************ TESTING *************
    # A simple main method to test off-line
    def main(args):
        test_client = AsipClient()
        test_client.process_input("@I,M,20{4:1,4:2,4:4,4:8,4:10,4:20,4:40,4:80,2:1,2:2,2:4,2:8,2:10,2:20,3:1,3:2,3:4,3:8,3:10,3:20}")
        test_client.process_input("@I,p,4,F")
        test_client.process_input("@I,p,4,10")
        test_client.process_input("@I,p,4,FF")