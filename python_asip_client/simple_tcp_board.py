__author__ = 'Gianluca Barbon'

import time
import sys
from asip_client import AsipClient
from threading import Thread
from queue import Queue
from asip_writer import AsipWriter
import socket
import struct

class SimpleTCPBoard:

    # ************   BEGIN CONSTANTS DEFINITION ****************

    DEBUG = True

    # ************   END CONSTANTS DEFINITION ****************

    # ************   BEGIN PRIVATE FIELDS DEFINITION ****************

    sock_conn = None  # self board uses socket
    asip = None  # The client for the aisp protocol
    queue = Queue(10)  # Buffer # TODO: use pipe instead of queue for better performances
    #  FIXME: fix Queue dimension?
    IPaddress = ""
    _TCPport = 6789

    # ************   END PRIVATE FIELDS DEFINITION ****************

    # self constructor takes the IP address
    # Here the tcp ip listener and the queue reader are started
    def __init__(self, IPaddress):
        try:
            self.IPaddress = IPaddress
            self.sock_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock_conn.connect((self.IPaddress, self._TCPport))

            self.asip = AsipClient(self.SimpleTCPWriter(self, sock_conn=self.sock_conn))
        except Exception as e:
            sys.stdout.write("Exception: caught {} while init tcp socket and asip protocols\n".format(e))

        try:
            # NOTICE: two request_port_mapping() are required. If this method is not called two times,
            # the client won't be able to set the pin mapping
            time.sleep(0.5)
            self.request_port_mapping()
            time.sleep(1)
            self.request_port_mapping()
            time.sleep(1)
            self.asip.set_auto_report_interval(0)
            self.ListenerThread(self.queue, self.sock_conn, True, self.DEBUG).start()
            self.ConsumerThread(self.queue, self.asip, True, self.DEBUG).start()
        except Exception as e:
            #TODO: improve exception handling
            sys.stdout.write("Exception: caught {} while launching threads\n".format(e))


    # ************ BEGIN PUBLIC METHODS *************

    # The following methods are just a replica from the asip class.
    # TODO: add parameter checikng in each function (raise exception?)
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

    #def open_serial(self, port, baudrate):

    def close_tcp_conn(self):
        self.sock_conn.close()

    # ************ END PRIVATE METHODS *************


    # ************ BEGIN PRIVATE CLASSES *************

    # As described above, SimpleTCPBoard writes messages to the tcp stream.
    # inner class SimpleTCPWriter implements abstract class AsipWriter:
    class SimpleTCPWriter(AsipWriter):
        parent = None
        sock_conn = None

        def __init__(self, parent, sock_conn):
            self.parent = parent
            self.sock_conn = sock_conn

        # val is a string
        # TODO: improve try catch
        def write(self, val):
            # TODO: insert a way to check weather the connection is still open or not
            try:
                if self.parent.DEBUG:
                   sys.stdout.write("DEBUG: sending {}\n".format(val))
                #temp = self.writeUTF(val)
                #self.sock_conn.sendall((val+'\n').encode('utf-8'))
                temp = val + '\r\n'
                #self.sock_conn.send(b"temp") # temp.encode('utf-8')
                self.sock_conn.sendall(bytes("hello tom\n",encoding='utf8'))
                # self.parent.sock_conn.send(val)
            except Exception as e:
                pass

        # def writeUTF(self, str):
        #     temp = None
        #     utf8 = str.encode('utf-8')
        #     length = len(utf8)
        #     temp.append(struct.pack('!H', length))
        #     format = '!' + str(length) + 's'
        #     temp.append(struct.pack(format, utf8))
        #     return temp

    # ListenerThread and ConsumerThread are implemented following the Producer/Consumer pattern
    # A class for a listener that read the tcp ip messages and put incoming messages on a queue
    # TODO: implement try catch
    class ListenerThread(Thread):

        queue = None
        sock_conn = None
        running = False
        DEBUG = False

        # overriding constructor
        def __init__(self, queue, sock_conn, running, debug):
            Thread.__init__(self)
            self.queue = queue
            self.sock_conn = sock_conn
            self.running = running
            self.DEBUG = debug
            if self.DEBUG:
                sys.stdout.write("DEBUG: listener thread process created \n")

        # if needed, kill will stops the loop inside run method
        def kill(self):
            self.running = False

        # overriding run method, thread activity
        def run(self):
            temp_buff = ""
            time.sleep(2)
            # TODO: implement ser.inWaiting() >= minMsgLen to check number of char in the receive buffer?

            while self.running:
                data = self.sock_conn.recv(512).decode('utf-8')
                data = data[2:]
                if not data:
                    pass
                else:
                    self.queue.put(data)
                    print("Received {}\n".format(data))
                # if self.DEBUG:
                #     sys.stdout.write("DEBUG: Temp buff is now {}\n".format(temp_buff))
                # val = self.sock_conn.recv(2)
                # if self.DEBUG:
                #     sys.stdout.write("DEBUG: val value when retrieving from tcp ip stream is {}\n".format(val))
                #
                # val = val.decode('utf-8')
                # time.sleep(0.1)
                # if self.DEBUG:
                #     sys.stdout.write("DEBUG: val value after decode is {}".format(val))
                # if val is not None and val!="\n":
                #     if "\n" in val:
                #         # If there is at least one newline, we need to process
                #         # the message (the buffer may contain previous characters).
                #
                #         while ("\n" in val and len(val) > 0):
                #             # But remember that there could be more than one newline in the buffer
                #             temp_buff += (val[0:val.index("\n")])
                #             self.queue.put(temp_buff)
                #             if self.DEBUG:
                #                 sys.stdout.write("DEBUG: tcp ip produced {}\n".format(temp_buff))
                #             temp_buff = ""
                #             val = val[val.index("\n")+1:]
                #             if self.DEBUG:
                #                 sys.stdout.write("DEBUG: Now val is {}\n".format(val))
                #         if len(val)>0:
                #             temp_buff = val
                #         if self.DEBUG:
                #             sys.stdout.write("DEBUG: After internal while buffer is {}\n".format(temp_buff))
                #     else:
                #         temp_buff += val
                #         if self.DEBUG:
                #             sys.stdout.write("DEBUG: else case, buff is equal to val, so they are {}\n".format(temp_buff))


    # A class that reads the queue and launch the processInput method of the AispClient.
    class ConsumerThread(Thread):

        queue = None
        asip = None
        running = False
        DEBUG = False

        # overriding constructor
        def __init__(self, queue, asip, running, debug):
            Thread.__init__(self)
            self.queue = queue
            self.asip = asip
            self.running = running
            self.DEBUG = debug
            if self.DEBUG:
                sys.stdout.write("DEBUG: consumer thread created \n")

        # if needed, kill will stops the loop inside run method
        def kill(self):
            self.running = False

        # overriding run method, thread activity
        def run(self):
            # global _queue
            # global asip
            while self.running:
                temp = self.queue.get()
                print("Consumer, calling process_input with input: {}\n".format(temp))
                self.asip.process_input(temp)
                self.queue.task_done()
                # if temp == "\n":
                    # print("WARNING")
                # print ("Consumed", temp)

    # ************ END PRIVATE CLASSES *************
