__author__ = 'Gianluca Barbon'

import sys
import struct

class PortManager:

    # ************   BEGIN CONSTANTS DEFINITION ****************
    __DEBUG = True # Do you want me to print verbose debug information?

    __MAX_NUM_DIGITAL_PINS = 72  # 9 ports of 8 pins at most?
    __MAX_NUM_ANALOG_PINS = 16  # Just a random number...

    __HIGH = 1
    __LOW = 0
    # ************   END CONSTANTS DEFINITION ****************

    # ************   BEGIN PRIVATE FIELDS DEFINITION ****************

    __digital_input_pins = []
    __analog_input_pins = []

    # We need to store that port x at position y corresponds to PIN z.
    # We store this as a map from port numbers (x) to another map position(y)->pin(z).
    # (see below the description of process_pin_mapping())
    # Notice that each board has its own port mapping.
    # Implemented as dictionary of dictionaries.
    __port_mapping = {}

    # ************   END PRIVATE FIELDS DEFINITION ****************

    # ************ BEGIN PUBLIC METHODS *************

    def __init__(self):
        pass

    def high_value(self):
        return self.__HIGH

    def low_value(self):
        return self.__LOW

    # I'm not sure we want this public... FIXME?
    def get_digital_pins(self):
        return self.__digital_input_pins

    def digital_read(self, pin):
        # FIXME: should add error checking here
        return self.__digital_input_pins[pin]

    def analog_read(self, pin):
        # FIXME: should add error checking here
        return self.__analog_input_pins[pin]

    # Method called only during the setup. At the beginning we receive a mapping of the form:
    # @I,M,20{4:1,4:2,4:4,4:8,4:10,4:20,4:40,4:80,2:1,2:2,2:4,2:8,2:10,2:20,3:1,3:2,3:4,3:8,3:10,3:20}
    # This means that there are 20 PINs; PIN 0 is mapped in position 0 of port 4 (4:1)
    # PIN 1 is mapped in position 1 (2^1) of port 4;
    # PIN 2 is mapped in position 2 (2^2) of port 4, i.e. 4:4;
    # ...
    # PIN 4 is mapped in position 4 (2^4=16=0x10) of port 4, i.e. 4:10;
    # PIN 9 is mapped in position 2 of port 2, i.e. 2:2, etc.
    # Old process_pin_mapping
    def process_pin_mapping(self, mapping):
        # FIXME: add error checking: check that the length corresponds to the number of PINs, etc.
        # if mapping not correct raise exception

        # Ports, pins, and services initialization
        self.__digital_input_pins = [None]*self.__MAX_NUM_DIGITAL_PINS
        self.__analog_input_pins = [None]*self.__MAX_NUM_ANALOG_PINS
        self.__port_mapping = None

        # For the moment I take the substring comprised between "{" and "}"
        # and I create an array of strings for each element.
        ports = mapping[mapping.index('{')+1:mapping.index('}')].split(',')

        # current pin index
        curr_pin = 0

        # port mapping init
        # iterate over 'ports' elements, getting each port:position
        for single_mapping in ports:
            port = int(single_mapping.split(":")[0])
            position = int(single_mapping.split(":")[1], 16)

            # If __port_mapping already contains something for this port,
            # we add the additional position mapping
            if port in self.__port_mapping:
                self.__port_mapping[port].update({position: curr_pin})
            # Otherwise, we create a new key in __port_mapping
            else:
                self.__port_mapping[port]= {position: curr_pin}
            curr_pin += 1

        if self.__DEBUG:
            #sys.stdout.write("DEBUG: Port bits to PIN numbers mapping: ")
            #sys.stdout.write("DEBUG: " + str(self.__port_mapping))
            sys.stdout.write("DEBUG: Port bits to PIN numbers mapping: {}".format(self.__port_mapping))

    # Method called every time a 'variation' in a pin is detected.
    # It process input messages for digital pins. We get a port and a sequence of bits.
    # The mapping between ports and pins is stored in __port_mapping.
    # See comments for __process_pin_mapping for additional details.
    # FIXME: add error checking for parameters
    # FIXME: check that no data arrives before __port_mapping has been created initialized!
    def process_port_data(self, input_str):

        port = int(input_str[5:6])
        #bitmask = int(input_str[7:7], 16)  # convert to base 16 returns problem with int() function
        bitmask = struct.unpack("h", input_str[7:7])[0] # convert to base 16

        if self.__DEBUG:
            # sys.stdout.write("DEBUG: process_port_data for port " + str(port) + " and bitmask " + str(bitmask))
            sys.stdout.write("DEBUG: process_port_data for port {} and bitmask {}".format(port,bitmask))

        single_port_map = self.__port_mapping[port] # map extraction for given port

        for (key, value) in single_port_map.items():
            if (key & bitmask) != 0x0:
                self.__digital_input_pins[value] = self.__HIGH
                if self.__DEBUG:
                    # sys.stdout.write("DEBUG: processPortData setting pin " + value + " to HIGH")
                    sys.stdout.write("DEBUG: processPortData setting pin {} to HIGH".format(value))
            else:
                self.__digital_input_pins[value] = self.__LOW
                if self.__DEBUG:
                    # sys.stdout.write("DEBUG: processPortData setting pin " + value + " to LOW")
                    sys.stdout.write("DEBUG: processPortData setting pin {} to LOW".format(value))

    # TODO: maybe merge this method with process_port_data
    def process_analog_data(self, input_str):
        if self.__DEBUG:
            # sys.stdout.write("DEBUG: analog received message " + input_str)
            sys.stdout.write("DEBUG: analog received message {}".format(input_str))

        # This is a list of strings "pin1:value1","pin2:value2",...
        try:
            pin_values = input_str[input_str.index("{")+1:input_str.index("}")].split(",")
            for pin_val in pin_values:
                pin_id = int(pin_val.split(":")[0])
                val = int(pin_val.split(":")[1])
                self.__analog_input_pins[pin_id] = val
                if self.__DEBUG:
                    # sys.stdout.write("DEBUG: setting analog pin " + str(pin_id) + " to " + str(val))
                    sys.stdout.write("DEBUG: setting analog pin {} to {}".format(pin_id, val))
        except Exception as e:
            if self.__DEBUG:
                #sys.stdout.write("DEBUG: exception while parsing analog message")
                #sys.stdout.write(e)
                sys.stdout.write("DEBUG: exception while parsing analog message {}".format(e))
                #traceback.print_exc()
        pass