__author__ = 'Gianluca Barbon'

import time
import sys
import glob
import serial
from asip_client import AsipClient
from threading import Thread
from asip_writer import AsipWriter
from serial import Serial
import threading


class SerialBoard:

    # ************   BEGIN CONSTANTS DEFINITION ****************

    DEBUG = False  # Activates debug messages
    __SERIAL_TIMEOUT = 2  # serial timeout (avoid blocking in case of issues)
    __PORT_INDEX_TO_OPEN = 0
    __BAUD_RATE = 57600

    # ************   END CONSTANTS DEFINITION ****************

    # ************   BEGIN PRIVATE FIELDS DEFINITION ****************

    # asip: The client for the asip protocol
    # __ser_conn: self board uses serial communication
    __ports = []  # serial ports array
    __threads = []  # List of threads

    # ************   END PRIVATE FIELDS DEFINITION ****************

    # Self constructor find the name of an active serial port and it creates a Serial objted
    def __init__(self):

        # Serial connection creation, AsipClient object creation
        try:
            self.__ser_conn = Serial()
            self.serial_port_finder(self.__PORT_INDEX_TO_OPEN)
            sys.stdout.write("Setting Serial: attempting to open {}\n".format(self.__ports[self.__PORT_INDEX_TO_OPEN]))
            self.open_serial(self.__ports[self.__PORT_INDEX_TO_OPEN], self.__BAUD_RATE)
            sys.stdout.write("Setting Serial: serial port {} opened\n".format(self.__ports[self.__PORT_INDEX_TO_OPEN]))
            self.asip = AsipClient(self.SimpleWriter(self.__ser_conn, self.DEBUG))
        except serial.SerialException as e:
            sys.stdout.write("Exception while init serial connection: {}\n".format(e))
            sys.exit(1)

        # Listener creation
        try:
            self.__threads.append(self.ListenerThread(self.asip, self.__ser_conn, self.DEBUG))
            sys.stdout.write("Creating Threads: starting\n")
            self.__threads[0].start()
            while not self.__threads[0].is_alive():  # checking that listener is alive
                pass
            sys.stdout.write("Creating Threads: all threads created and alive\n")
        except Exception as e:
            sys.stdout.write("Caught exception in threads launch: {}\n".format(e))
            self.thread_killer()
            sys.exit(1)
        else:
            # Running
            try:
                # TODO: version checking still mis
                # flag will be set to true when valid version message is received
                # while self.asip.isVersionOk() == False:
                #     self.asip.request_info()
                #     time.sleep(1.0)sing
                # Checking mapping
                while not self.asip.check_mapping():
                    self.asip.request_port_mapping()
                    time.sleep(0.5)
                self.asip.set_auto_report_interval(100)
                sys.stdout.write("Creating Threads: Mapping received, auto-report interval set to 0. Running now!\n")
            except KeyboardInterrupt:  # KeyboardInterrupt handling in order to close every thread correctly
                sys.stdout.write("KeyboardInterrupt while checking mapping. Attempting to close listener thread.\n")
                self.thread_killer()
                sys.exit()
            except Exception as e:  # killing threads and exiting in case of generic exception
                sys.stdout.write("Caught generic exception while checking mapping: {}\n".format(e))
                self.thread_killer()
                sys.exit(1)

    # ************ BEGIN PUBLIC METHODS *************

    # stops and wait for the join for threads in the given pool
    # TODO: improve in case of timeout of the join
    def thread_killer(self):
        for i in self.__threads:
            try:
                i.stopper()
                sys.stdout.write("Killing Threads: event for {} successfully set\n".format(i))
            except Exception as e:
                sys.stdout.write("Caught exception while stropping thread {}.\nException is: {}\n".format(i, e))
        time.sleep(0.5)
        sys.stdout.write("Killing Threads: waiting for join\n")
        for i in self.__threads:
            i.join()
            sys.stdout.write("Killing Threads: thread {} successfully closed\n".format(i))
        self.__threads = []
        sys.stdout.write("All threads terminated.\n")
        return True

    def get_asip_client(self):
        return self.asip

    # ************ END PUBLIC METHODS *************

    # ************ BEGIN PRIVATE METHODS *************

    def open_serial(self, port, baud_rate):
        if self.__ser_conn.isOpen():
            self.__ser_conn.close()
        self.__ser_conn.port = port
        self.__ser_conn.baudrate = baud_rate
        self.__ser_conn.timeout = self.__SERIAL_TIMEOUT
        self.__ser_conn.open()
        # Toggle DTR to reset Arduino
        self.__ser_conn.setDTR(False)
        time.sleep(1)
        # toss any data already received, see
        self.__ser_conn.flushInput()
        time.sleep(1)
        self.__ser_conn.setDTR(True)
        time.sleep(1)

    def close_serial(self):
        self.__ser_conn.close()

    # This methods retrieves the operating system and set the Arduino serial port
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    # TODO: test needed for linux and windows implementation
    # TODO: improve try except
    def serial_port_finder(self, desired_index):

        system = sys.platform
        if system.startswith('win'):
            temp_ports = ['COM' + str(i + 1) for i in range(255)]
        elif system.startswith('linux'):
            # this is to exclude your current terminal "/dev/tty"
            temp_ports = glob.glob('/dev/tty[A-Za-z]*')
        elif system.startswith('darwin'):
            temp_ports = glob.glob('/dev/tty.usbmodem*')
            cp2104 = glob.glob('/dev/tty.SLAB_USBtoUART')  # append usb to serial converter cp2104
            ft232rl = glob.glob('/dev/tty.usbserial-A9MP5N37')  # append usb to serial converter ft232rl
            fth = glob.glob('/dev/tty.usbserial-FTHI5TLH')  # append usb to serial cable
            #new = glob.glob('/dev/tty.usbmodemfd121')
            #temp_ports = glob.glob('/dev/tty.SLAB_USBtoUART')
            #temp_ports = glob.glob('/dev/tty.usbserial-A9MP5N37')
            if cp2104 is not None:
                temp_ports += cp2104
            if ft232rl is not None:
                temp_ports += ft232rl
            if fth is not None:
                temp_ports += fth
            #if new is not None: # FIXME: REMOVE!!! Only used for tests
            #    temp_ports = new
        else:
            raise EnvironmentError('Unsupported platform')

        for port in temp_ports:
            try:
                self.__ser_conn.port = port
                self.__ser_conn.open()
                self.__ser_conn.close()
                self.__ports.append(port)
                if len(self.__ports) > desired_index:
                    return  # we have found the desired port
            except serial.SerialException:
                pass
        if self.DEBUG:
            sys.stdout.write("DEBUG: available ports are {}\n".format(self.__ports))

    # ************ END PRIVATE METHODS *************

    # ************ BEGIN PRIVATE CLASSES *************

    # As described above, SimpleSerialBoard writes messages to the serial port.
    # inner class SimpleWriter implements abstract class AsipWriter:
    class SimpleWriter(AsipWriter):

        def __init__(self, ser_conn, debug=False):
            self.ser_conn = ser_conn
            self.DEBUG = debug

        # val is a string
        # TODO: improve try catch, add exit in case of exception too
        def write(self, val):
            if self.ser_conn.isOpen():
                try:
                    temp = val.encode()
                    self.ser_conn.write(temp)
                    if self.DEBUG:
                        sys.stdout.write("DEBUG: just wrote in serial {}\n".format(temp))
                except (OSError, serial.SerialException) as e:
                    sys.stdout.write("Caught exception in serial write: {}\n".format(e))
            else:
                raise serial.SerialException

    # ListenerThread read the serial stream and call process_input
    class ListenerThread(Thread):

        # overriding constructor
        def __init__(self, asip, ser_conn, debug=False):
            Thread.__init__(self)
            self.asip = asip
            self.ser_conn = ser_conn
            self.DEBUG = debug
            self._stopper = threading.Event()
            sys.stdout.write("Listener Thread: thread process created.\n")

        # if needed, kill will stops the loop inside run method
        def stopper(self):
            sys.stdout.write("Listener Thread: now stopping.\n")
            self._stopper.set()

        # overriding run method, thread activity
        def run(self):
            time.sleep(2)  # TODO: maybe reduce this sleep?
            sys.stdout.write("Listener Thread: now running.\n")
            ser_buffer = ""
            while not self._stopper.is_set():
                try:
                    c = self.ser_conn.read()  # attempt to read a character from Serial
                    c = c.decode('utf-8', errors='ignore')
                    if len(c) == 0:  # was anything read?
                        pass
                    else:
                        # if self.DEBUG:
                        #    sys.stdout.write("DEBUG: Char from serial: {}\n".format(c))
                        if c == '\n' or c == '\n':
                            if len(ser_buffer) > 0:
                                ser_buffer += '\n'
                                self.asip.process_input(ser_buffer)
                                if self.DEBUG:
                                    sys.stdout.write("DEBUG: Complete message from serial: {}\n".format(ser_buffer))
                            ser_buffer = ""
                        else:
                            ser_buffer += c
                except serial.SerialTimeoutException:
                    continue  # Go to next iteration in case of serial timeout
                except serial.SerialException as e:
                    sys.stdout.write(
                        "Caught SerialException in serial read: {}\nListener Thread will now stop\n".format(e))
                    self.stopper()
                except Exception as e:
                    sys.stdout.write("Caught exception: {}\nListener Thread will NOT stop\n".format(e))
                    #self.stopper()

            sys.stdout.write("Listener Thread: stopped\n")

    # ************ END PRIVATE CLASSES *************)
