__author__ = 'Gianluca Barbon'

import asip_writer
import time
import sys
import random
from asip_client import AsipClient
from threading import Thread
from queue import Queue
from asip_writer import AsipWriter
# import services.AsipService
from serial import Serial


class SimpleSerialBoard:

    # ************   BEGIN CONSTANTS DEFINITION ****************

    DEBUG = False

    # ************   END CONSTANTS DEFINITION ****************

    # ************   BEGIN PRIVATE FIELDS DEFINITION ****************

    # self board uses serial communication
    ser_conn = None

    # The client for the aisp protocol
    asip = None

    # Buffer
    queue = Queue(10) # TODO: use pipe instead of queue for better performances
    # FIXME: fix Queue dimension?

    # ************   END PRIVATE FIELDS DEFINITION ****************

    # self constructor takes the name of the serial port and it
    # creates the serialPort object.
    # We attach a listener to the serial port with SerialPortReader  self
    # listener calls the aisp method to process input.
    def __init__(self, port):

        # FIXME: very simple implementation!
        # self.serial_port = SerialPort(port) # class serial port does not exist
        self.ser_conn = Serial(port='/dev/cu.usbmodemfd121', baudrate=57600)
        self.asip = AsipClient(self.SimpleWriter(self))

        # try:
        #     serialPort.openPort() # Open port
        #     serialPort.setParams(57600, 8, 1, 0)
        #     serialPort.setDTR(false)
        #     Thread.sleep(250)
        #     serialPort.setDTR(true)
        #     # Set params
        #     int mask = SerialPort.MASK_RXCHAR   #+ SerialPort.MASK_CTS
        #             # + SerialPort.MASK_DSR # Prepare mask
        #     serialPort.setEventsMask(mask) # Set mask
        #  catch (Exception ex):
        #     System.out.println(ex)

        try:
            # Thread.sleep(1500)
            # requestPortMapping()
            # Thread.sleep(500)
            # requestPortMapping()
            # Thread.sleep(500)
            # requestPortMapping()
            # Thread.sleep(500)
            self.request_port_mapping()
            time.sleep(0.5)
            self.request_port_mapping()
            time.sleep(0.5)
            self.request_port_mapping()
            time.sleep(0.5)
            self.ListenerThread(self.queue, self.ser_conn, self.DEBUG).start()
            self.ConsumerThread(self.queue, self.asip, self.DEBUG).start()
        except Exception as e:
            print(e) #TODO: improve exception handling


    # ************ BEGIN PUBLIC METHODS *************

    # The following methods are just a replica from the asip class.
    def digital_read(self, pin):
        return self.asip.digital_read(pin)

    def analog_read(self, pin):
        return self.asip.analog_read(pin)

    def set_pin_mode(self, pin, mode):
        self.asip.set_pin_mode(pin, mode)

    def digital_write(self, pin, value):
        self.asip.digital_write(pin, value)

    def analog_write(self, pin, value):
        self.asip.analog_write(pin, value)

    def request_port_mapping(self):
        self.asip.request_port_mapping()

    def set_auto_report_interval(self, interval):
        self.asip.set_auto_report_interval(interval)

    def add_service(self, service_id, asip_service):
        self.asip.add_service(service_id, asip_service)

    def get_asip_client(self):
        return self.asip

    # ************ END PUBLIC METHODS *************


    # ************ BEGIN PRIVATE METHODS *************

    # ************ END PRIVATE METHODS *************


    # ************ BEGIN PRIVATE CLASSES *************

    # As described above, SimpleSerialBoard writes messages to the serial port.
    # inner class SimpleWriter implements abstract class AsipWriter:
    class SimpleWriter(AsipWriter):
        parent = None

        def __init__(self, parent):
            self.parent = parent

        # val is a string
        def write(self, val):
            # global ser_conn
            self.parent.ser_conn.write(val.encode())
            # TODO: implement try catch

    # A class for a listener that calls the processInput method of the AispClient.
    # class SerialPortReader implements SerialPortEventListener:

    class ListenerThread(Thread):

        queue = None
        ser_conn = None
        DEBUG = None

        def __init__(self, queue, ser_conn, DEBUG):
            Thread.__init__(self)
            self.queue = queue
            self.ser_conn = ser_conn
            self.DEBUG = DEBUG

        def run(self):
            temp_buff = ""
            # global serial
            time.sleep(2)
            nums = range(5)
            # global _queue
            while True:
                # num = random.choice(nums)
                if self.DEBUG:
                    sys.stdout.write("DEBUG: Temp buff is now {}\n".format(temp_buff))
                val = self.ser_conn.readline()
                if self.DEBUG:
                    sys.stdout.write("DEBUG: val value when retrieving from serial is {}\n".format(val))
                val = val.decode('utf-8')
                if self.DEBUG:
                    sys.stdout.write("DEBUG: val value after decode is {}".format(val))
                # if val != None:
                if val != None and val!="\n":
                    if "\n" in val:
                        # If there is at least one newline, we need to process
                        # the message (the buffer may contain previous characters).

                        while ("\n" in val and len(val) > 0):
                            # But remember that there could be more than one newline in the buffer
                            temp_buff += (val[0:val.index("\n")])
                            self.queue.put(temp_buff)
                            if self.DEBUG:
                                sys.stdout.write("DEBUG: Serial produced {}\n".format(temp_buff))
                            temp_buff = ""
                            val = val[val.index("\n")+1:]
                            if self.DEBUG:
                                sys.stdout.write("DEBUG: Now val is {}\n".format(val))
                            # self.asip.process_input()
                        if len(val)>0:
                            temp_buff = val
                        if self.DEBUG:
                            sys.stdout.write("DEBUG: After internal while buffer is {}\n".format(temp_buff))
                    else:
                        temp_buff += val
                        if self.DEBUG:
                            sys.stdout.write("DEBUG: else case, buff is equal to val, so they are {}\n".format(temp_buff))
                #time.sleep(random.random())


    class ConsumerThread(Thread):

        queue = None
        DEBUG = None
        asip = None

        def __init__(self, queue, asip, DEBUG):
            Thread.__init__(self)
            self.queue = queue
            self.DEBUG = DEBUG
            self.asip = asip

        def run(self):
            # global _queue
            # global asip
            while True:
                temp = self.queue.get()
                self.asip.process_input(temp)
                self.queue.task_done()
                # if temp == "\n":
                    # print("WARNING")
                # print ("Consumed", temp)
                # time.sleep(random.random())
    # ************ END PRIVATE CLASSES *************