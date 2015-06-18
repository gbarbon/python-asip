__author__ = 'Gianluca Barbon'

import time
import sys
from asip_client import AsipClient
from threading import Thread
from asip_writer import AsipWriter
import paho.mqtt.client as mqtt
import threading


class MQTTBoard:

    # ************   BEGIN CONSTANTS DEFINITION ****************

    DEBUG = True  # Activates debug messages
    __TCP_port = 1883  # MQTT registered port

    # ************   END CONSTANTS DEFINITION ****************

    # ************   BEGIN PRIVATE FIELDS DEFINITION ****************

    # asip: The client for the asip protocol
    # mqtt_client: self board uses mqtt
    __threads = []  # List of threads

    # ************   END PRIVATE FIELDS DEFINITION ****************

    # self constructor takes the broker address and the target board
    # client name and keepalive are optional parameters
    def __init__(self, broker_ip, target_board, my_name="Client", keepalive=180):

        # setting mqtt connection and asip protocol
        try:
            sys.stdout.write("Setting mqtt: attempting to connect to broker {}\n".format(broker_ip))
            self.__Broker = broker_ip
            self.__keepalive = keepalive
            self.__SUBTOPIC = "asip/"+target_board+"/in"
            self.__PUBTOPIC = "asip/"+target_board+"/out"

            self.mqtt_client = mqtt.Client(my_name)
            self.mqtt_client.on_connect = self.on_connect
            self.connect()

            self.asip = AsipClient(self.SimpleMQTTWriter(self.mqtt_client, self.__PUBTOPIC, self.DEBUG))
        except Exception as e:
            sys.stdout.write("Exception caught in init mqtt and asip protocols: {}\n".format(e))
            try:  # try to close connection
                self.disconnect()
            except Exception as e:
                sys.stdout.write("Caught generic exception while disconnecting MQTT: {}\n".format(e))
            finally:
                sys.exit(1)

        # Listener creation
        try:
            self.__threads.append(self.ListenerThread(
                self.asip, self.mqtt_client, self.__SUBTOPIC, self.DEBUG))
            sys.stdout.write("Creating Threads: starting\n")
            self.__threads[0].start()
            while not self.__threads[0].is_alive():  # checking that listener is alive
                pass
            sys.stdout.write("Creating Threads: all threads created and alive\n")

            self.mqtt_client.loop_start()  # starting mqtt loop

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
            self.disconnect()
        except Exception as e:
            sys.stdout.write("Caught generic exception while disconnecting MQTT: {}\n".format(e))
        sys.stdout.write("All threads terminated.\n")
        return True

    def get_asip_client(self):
        return self.asip

    # ************ END PUBLIC METHODS *************

    # ************ BEGIN PRIVATE METHODS *************

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        if self.DEBUG:
            sys.stdout.write("Connected with result code: {}\n".format(rc))

    def connect(self):
        self.mqtt_client.connect(self.__Broker, self.__TCP_port, self.__keepalive)
        sys.stdout.write("Connected to MQTT broker: {}  port: {} keepalive: {} .\n"
                         .format(self.__Broker, self.__TCP_port, self.__keepalive))

    def disconnect(self):
        self.mqtt_client.disconnect()
        sys.stdout.write("Disconnected from MQTT broker.\n")

    # ************ END PRIVATE METHODS *************

    # ************ BEGIN PRIVATE CLASSES *************

    # SimpleMQTTBoard writes messages to the MQTT stream.
    # inner class SimpleMQTTWriter implements abstract class AsipWriter:
    class SimpleMQTTWriter(AsipWriter):

        def __init__(self, mqtt_client, pubtopic, debug=False):
            self.mqtt_client = mqtt_client
            self.pubtopic = pubtopic
            self.DEBUG = debug

        # val is a string
        # TODO: improve try catch
        def write(self, val):
            # TODO: insert a way to check weather the connection is still open or not
            try:
                self.mqtt_client.publish(self.pubtopic, val)
                if self.DEBUG:
                    sys.stdout.write("DEBUG: sent {}\n".format(val))
            except Exception as e:
                sys.stdout.write("Caught exception in MQTT publish: {}\n".format(e))

    # ListenerThread read the mqtt stream and call process_input
    class ListenerThread(Thread):

        # overriding constructor
        def __init__(self, asip, mqtt_client, subtopic, debug=False):
            Thread.__init__(self)
            self.asip = asip
            self.mqtt_client = mqtt_client
            self.mqtt_client.on_message = self.on_message  # callback
            self.DEBUG = debug
            self.listener_buffer = ""
            self.mqtt_client.subscribe(topic=subtopic)
            sys.stdout.write("Listener Thread: subscribed to topic: {} .\n".format(subtopic))
            self._stopper = threading.Event()
            sys.stdout.write("Listener Thread: thread process created.\n")

        # if needed, kill will stops the loop inside run method
        def stopper(self):
            sys.stdout.write("Listener Thread: now stopping.\n")
            self._stopper.set()

        # The callback for when a PUBLISH message is received from the server.
        def on_message(self, client, userdata, msg):
            try:
                if not msg.payload:
                    pass
                else:
                    data = msg.payload.decode('utf-8')
                    if data != '\r' and data != '\n' and data != ' ':  # ignore empty lines
                        self.listener_buffer += data
                    if self.DEBUG:
                        sys.stdout.write("DEBUG: Received {}\n".format(data))
            except Exception as e:
                sys.stdout.write("Exception in listener on_message method: {}\nListener will now stop\n".format(e))
                self.stopper()

        # overriding run method, thread activity
        def run(self):
            time.sleep(2)  # TODO: maybe reduce this sleep?
            sys.stdout.write("Listener Thread: now running.\n")
            while not self._stopper.is_set():
                time.sleep(0.001)  # TODO: thread concurrency
                try:
                    # If there is at least one newline, we need to process the message
                    # (the buffer may contain previous characters).
                    while "\n" in self.listener_buffer:
                        temp = self.listener_buffer[0:self.listener_buffer.index("\n")]
                        self.asip.process_input(temp)
                        self.listener_buffer = self.listener_buffer[self.listener_buffer.index("\n")+1:]
                except Exception as e:
                    sys.stdout.write("Exception in listener run method: {}\nListener will now stop\n".format(e))
                    self.stopper()

            sys.stdout.write("Listener Thread: stopped\n")

    # ************ END PRIVATE CLASSES *************