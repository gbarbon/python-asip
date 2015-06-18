__author__ = 'Gianluca Barbon'

import time
import sys
from asip_client import AsipClient
from threading import Thread
import threading
from asip_writer import AsipWriter
import socket
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

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
    #_TCPport = 6789 # the one used by the java bridge by franco in mirto
    _TCPport = 5005

    # ************   END PRIVATE FIELDS DEFINITION ****************

    # self constructor takes the IP address
    # Here the tcp ip listener and the queue reader are started
    def __init__(self, IPaddress):
        try:
            self.IPaddress = IPaddress
            sys.stdout.write("Attempting to connect to {} and port {}\n".format(self.IPaddress, self._TCPport))
            self.sock_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock_conn.connect((self.IPaddress, self._TCPport))
            self.asip = AsipClient(self.SimpleTCPWriter(self, sock_conn=self.sock_conn))
        except Exception as e:
            sys.stdout.write("Exception caught in init tcp socket and asip protocols {}\n".format(e))
        else:
            worker = []
            try:
                # NOTICE: two request_port_mapping() are required. If this method is not called two times,
                # the client won't be able to set the pin mapping
                worker.append(self.ListenerThread(self.queue, self.sock_conn, True, self.DEBUG))
                worker.append(self.ConsumerThread(self.queue, self.asip, True, self.DEBUG))
                for i in worker:
                    if self.DEBUG:
                        print("Starting {}".format(i))
                    i.start()
                all_alive = False
                while not all_alive: # cheching that every thread is alive
                    # TODO: improve syntax in following line
                    if worker[0].is_alive() and worker[1].is_alive():
                        all_alive = True

                # TODO: check following code
                # while self.asip.isVersionOk() == False:  # flag will be set to true when valid version message is received
                #     self.request_info()
                #     time.sleep(1.0)
                active_workers = threading.active_count()
                sys.stdout.write("*** All threads created and alive ***\n")
            except Exception as e:
                sys.stdout.write("Caught exception in thread launch: {}\n".format(e))
                self.close_tcp_conn()
                self.thread_killer(worker)
                sys.exit(1)
            else:
                try:

                    while not self.asip.check_mapping():
                        self.request_port_mapping()
                        time.sleep(0.25)
                    self.set_auto_report_interval(0)
                    # checking that a thread is not killed by an exception
                    while len(threading.enumerate()) == active_workers:
                        pass
                # KeyboardInterrupt handling in order to close every thread correctly
                except KeyboardInterrupt:
                    sys.stdout.write("KeyboardInterrupt: attempting to close threads.\n")
                finally:
                    # killing thread in both cases: keyboardinterrupt or exception in one of the thread
                    self.close_tcp_conn()
                    self.thread_killer(worker)
                    sys.stdout.write("All terminated.\n")
                    sys.exit()

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

    def request_info(self):
        self.asip.request_info()

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

    # stops and wait for the join for threads in the given pool
    # TODO: improve in case of timeout of the join
    def thread_killer(self, thread_pool):
        for i in thread_pool:
            i.stop()
            if self.DEBUG:
                sys.stdout.write("Event for {} successfully set\n".format(i))
        sys.stdout.write("Waiting for join\n")
        for i in thread_pool:
            i.join()
            if self.DEBUG:
                sys.stdout.write("Thread {} successfully closed\n".format(i))
        return True

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
                #if self.parent.DEBUG:
                   #sys.stdout.write("DEBUG: sending {}\n".format(val))
                #temp = self.writeUTF(val)
                #self.sock_conn.sendall((val+'\n').encode('utf-8'))
                temp = val #+ '\n'
                #self.sock_conn.send(b"temp") # temp.encode('utf-8')
                #self.sock_conn.sendall(bytes(temp,encoding='utf8'))
                # self.parent.sock_conn.send(val)
                #temp.encode('utf-8')
                self.sock_conn.send(temp)
                if self.parent.DEBUG:
                   sys.stdout.write("DEBUG: sent {}\n".format(temp))
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
        BUFFER_SIZE = 256

        # overriding constructor
        def __init__(self, queue, sock_conn, running, debug):
            Thread.__init__(self)
            self.queue = queue
            self.sock_conn = sock_conn
            self.running = running
            self.DEBUG = debug
            self._stop = threading.Event()
            if self.DEBUG:
                sys.stdout.write("DEBUG: listener thread process created \n")

        # if needed, kill will stops the loop inside run method
        def stop(self):
            self._stop.set()

        # overriding run method, thread activity
        def run(self):
            temp_buff = ""
            time.sleep(2)
            write_buffer = ""
            # TODO: implement ser.inWaiting() >= minMsgLen to check number of char in the receive buffer?

            while not self._stop.is_set():
                # data = self.sock_conn.recv(512).decode('utf-8')
                # #data = data[2:]
                # if not data:
                #     pass
                # else:
                #     self.queue.put(data)
                #     print("Received {}\n".format(data))



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

                data = self.sock_conn.recv(self.BUFFER_SIZE)
                # print("Received data is: {}".format(data))
                if data != '\r' and data != '\n' and data !=' ' and data is not None: # ignore empty lines
                    if "\n" in data:
                        # If there is at least one newline, we need to process
                        # the message (the buffer may contain previous characters).
                        while ("\n" in data and len(data) > 0):
                            # But remember that there could be more than one newline in the buffer
                            write_buffer += (data[0:data.index("\n")])
                            temp = write_buffer.encode()
                            self.queue.put(temp)
                            #print("Inserting in queue {}".format(temp))
                            write_buffer = ""
                            if data[data.index("\n")+1:]=='\n':
                                data = ''
                                break
                            else:
                                data = data[data.index("\n")+1:]
                        if len(data)>0 and data not in ('\r','\n',' '):
                            write_buffer = data
                    else:
                        write_buffer += data


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
            self._stop = threading.Event()
            if self.DEBUG:
                sys.stdout.write("DEBUG: consumer thread created \n")

        # if needed, kill will stops the loop inside run method
        def stop(self):
            self._stop.set()

        # overriding run method, thread activity
        def run(self):
            # global _queue
            # global asip
            while not self._stop.is_set():
                temp = self.queue.get()
                # print("Consumer, calling process_input with input: {}\n".format(temp))
                self.asip.process_input(temp)
                self.queue.task_done()
                # if temp == "\n":
                    # print("WARNING")
                # print ("Consumed", temp)

    # ************ END PRIVATE CLASSES *************
