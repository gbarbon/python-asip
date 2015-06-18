__author__ = 'Gianluca Barbon'

from asip_client import AsipClient
from asip_writer import AsipWriter
import threading
from threading import Thread
import socket
import time
import sys


class TCPBoard:

    # ************   BEGIN CONSTANTS DEFINITION ****************

    DEBUG = True  # Activates debug messages
    __BUFFER_SIZE = 256  # TCP buffer size
    __RECV_TIMEOUT = 2  # socket receive timeout in second

    # ************   END CONSTANTS DEFINITION ****************

    # ************   BEGIN PRIVATE FIELDS DEFINITION ****************

    # asip: The client for the asip protocol
    # __sock_conn: tcp/ip socket communication
    __threads = []  # List of threads

    # ************   END PRIVATE FIELDS DEFINITION ****************

    # tcp_port = 6789 is the one used by the java bridge by franco in mirto
    def __init__(self, ip_address='127.0.0.1', tcp_port=5005):
        try:
            sys.stdout.write("Setting tcp: attempting to connect to {} and port {}\n".format(ip_address, tcp_port))
            self.__sock_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock_conn.connect((ip_address, tcp_port))
            self.asip = AsipClient(self.SimpleTCPWriter(self.__sock_conn, self.DEBUG))
        except Exception as e:
            sys.stdout.write("Exception caught in init tcp socket and asip protocols {}\n".format(e))
            try:  # try to close connection
                self.close_tcp_conn()
            finally:
                sys.exit(1)

        # Listener creation
        try:
            self.__threads.append(self.ListenerThread(
                self.asip, self.__sock_conn, self.__RECV_TIMEOUT, self.__BUFFER_SIZE, self.DEBUG))
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
                # TODO: version checking still missing
                # flag will be set to true when valid version message is received
                # while self.asip.isVersionOk() == False:
                #     self.asip.request_info()
                #     time.sleep(1.0)
                # Checking mapping
                while not self.asip.check_mapping():
                    self.asip.request_port_mapping()
                    time.sleep(0.5)
                self.asip.set_auto_report_interval(0)
                sys.stdout.write("Creating Threads: Mapping received, auto-report interval set to 0. Running now!\n")

           # KeyboardInterrupt handling in order to close every thread correctly
            except KeyboardInterrupt:  # KeyboardInterrupt handling in order to close every thread correctly
                sys.stdout.write("KeyboardInterrupt while checking mapping. Attempting to close listener thread.\n")
                self.thread_killer()
                sys.exit()
            except Exception as e:  # killing threads and exiting in case of generic exception
                sys.stdout.write("Caught generic exception while checking mapping: {}\n".format(e))
                self.thread_killer()
                sys.exit(1)

    # ************ BEGIN PUBLIC METHODS *************

    # stops and waits for the join for threads in the given pool
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
        try:
            self.close_tcp_conn()
        except Exception as e:
            sys.stdout.write("Caught generic exception while calling close_tcp_conn: {}\n".format(e))
        sys.stdout.write("All threads terminated.\n")
        return True

    def get_asip_client(self):
        return self.asip

    # ************ END PUBLIC METHODS *************

    # ************ BEGIN PRIVATE METHODS *************

    def close_tcp_conn(self):
        self.__sock_conn.shutdown(socket.SHUT_RDWR)
        self.__sock_conn.close()
        sys.stdout.write("Connection closed.\n")

    # ************ END PRIVATE METHODS *************

    # ************ BEGIN PRIVATE CLASSES *************

    # As described above, SimpleTCPBoard writes messages to the tcp stream.
    # inner class SimpleTCPWriter implements abstract class AsipWriter:
    class SimpleTCPWriter(AsipWriter):

        def __init__(self, sock_conn, debug=False):
            self.sock_conn = sock_conn
            self.DEBUG = debug

        # val is a string
        # TODO: improve try catch
        def write(self, val):
            # TODO: insert a way to check weather the connection is still open or not
            try:
                self.sock_conn.send(val)
                if self.DEBUG:
                    sys.stdout.write("DEBUG: sent {}\n".format(val))
            except Exception as e:
                sys.stdout.write("Caught exception in serial write: {}\n".format(e))

    # ListenerThread read the tcp/ip stream and call process_input
    class ListenerThread(Thread):

        # overriding constructor
        def __init__(self, asip, sock_conn, timeout, buffer_size=256, debug=False):
            Thread.__init__(self)
            self.asip = asip
            self.sock_conn = sock_conn
            self.sock_conn.settimeout(timeout)  # setting socket recv timeout
            self.BUFFER_SIZE = buffer_size
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
            temp_buffer = ""
            while not self._stopper.is_set():
                try:
                    data = self.sock_conn.recv(self.BUFFER_SIZE)
                    # sys.stdout.write("Received data is: {}\n".format(data))
                    if data != '\r' and data != '\n' and data != ' ' and data is not None:  # ignore empty lines
                        if "\n" in data:
                            # If there is at least one newline, we need to process
                            # the message (the buffer may contain previous characters).
                            while "\n" in data and len(data) > 0:
                                # But remember that there could be more than one newline in the buffer
                                temp_buffer += (data[0:data.index("\n")])
                                temp = temp_buffer.encode()
                                self.asip.process_input(temp)
                                temp_buffer = ""
                                if data[data.index("\n")+1:] == '\n':
                                    data = ''
                                    break
                                else:
                                    data = data[data.index("\n")+1:]
                            if len(data) > 0 and data not in ('\r', '\n', ' '):
                                temp_buffer = data
                        else:
                            temp_buffer += data
                except socket.timeout as e:
                    err = e.args[0]
                    if err == 'timed out':  # socket time out, if the _stop value is set, program will exit
                        continue
                except Exception as e:
                    sys.stdout.write("Caught exception in listener: {}\nListener will now stop\n".format(e))
                    self.stopper()

            sys.stdout.write("Listener Thread: stopped\n")

    # ************ END PRIVATE CLASSES *************