__author__ = 'Gianluca Barbon'

import time
import sys
from asip_client import AsipClient
from threading import Thread
try:
    from Queue import Queue
except ImportError:
    from queue import Queue
from asip_writer import AsipWriter
import paho.mqtt.client as mqtt


class SimpleMQTTBoard:

    # ************   BEGIN CONSTANTS DEFINITION ****************

    DEBUG = True

    # ************   END CONSTANTS DEFINITION ****************

    # ************   BEGIN PRIVATE FIELDS DEFINITION ****************

    mqtt_client = None  # self board uses mqtt
    asip = None  # The client for the aisp protocol
    queue = Queue(10)  # Buffer # TODO: use pipe instead of queue for better performances
    #  FIXME: fix Queue dimension?
    Broker = ""
    _TCPport = 1883
    _ClientID = ""
    _SUBTOPIC = ""
    _PUBTOPIC = ""

    # ************   END PRIVATE FIELDS DEFINITION ****************

    # self constructor takes the Broker address
    # Here the listener and the queue reader are started
    def __init__(self, Broker, BoardID):
        try:
            self.Broker = Broker
            self._ClientID = "Client"
            self._SUBTOPIC = "asip/"+BoardID+"/out"
            self._PUBTOPIC = "asip/"+BoardID+"/in"

            self.mqtt_client = mqtt.Client(self._ClientID)
            self.mqtt_client.on_connect = self.on_connect
            self.connect()
            self.buffer = ""

            self.asip = AsipClient(self.SimpleMQTTWriter(self))
        except Exception as e:
            sys.stdout.write("Exception: caught {} while init tcp socket and asip protocols\n".format(e))

        try:
            # NOTICE: two request_port_mapping() are required. If this method is not called two times,
            # the client won't be able to set the pin mapping
            # time.sleep(0.5)
            # self.request_port_mapping()
            # time.sleep(1)
            # self.request_port_mapping()
            # time.sleep(1)

            # ListenerThread is the one that reads incoming messages from mqtt
            # ConsumerThread is the one that read the queue filled by ListenerThread and call the asip process_input
            # Sender is the thread that publish messages
            self.ListenerThread(self.queue, self.mqtt_client, True, self.DEBUG, self._SUBTOPIC).start()
            self.ConsumerThread(self.queue, self.asip, True, self.DEBUG).start()
            self.Sender(self).start()

            self.mqtt_client.loop_start() # starting mqtt loop

            # TODO: check following code
            # while self.asip.isVersionOk() == False:  # flag will be set to true when valid version message is received
            #     self.request_info()
            #     time.sleep(1.0)
            while not self.asip.check_mapping():
                print("Requesting mapping")
                self.request_port_mapping()
                time.sleep(0.25)
            sys.stdout.write("**** Everything check ****\n")
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

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        if self.DEBUG:
            sys.stdout.write("DEBUG: Connected with result code {}".format(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        #self.mqtt_client.subscribe("$SYS/#")
        #self.mqtt_client.subscribe(self._SUBTOPIC)

    def connect(self):
        if self.DEBUG:
            sys.stdout.write("DEBUG: Connecting to mqtt broker {} on port {}".format(self.Broker,self._TCPport))
        self.mqtt_client.connect(self.Broker, self._TCPport, 180)

    def sendData(self, msg):
        self.mqtt_client.publish(self._PUBTOPIC, msg)

    def disconnect(self):
        if self.DEBUG:
            sys.stdout.write("DEBUG: DEBUG: Disconnected from mqtt")
        self.mqtt_client.disconnect()

    # ************ END PRIVATE METHODS *************


    # ************ BEGIN PRIVATE CLASSES *************

    class Sender(Thread):
        def __init__(self, parent):
            Thread.__init__(self)
            self.parent = parent
            self.running = True

        def run(self):
            while self.running:
                if not self.parent.buffer:
                    pass
                else:
                    if self.parent.DEBUG:
                        sys.stdout.write("DEBUG: Sending: {}\n".format(self.parent.buffer[0:self.parent.buffer.index('\n')]))
                    self.parent.mqtt_client.publish(self.parent._PUBTOPIC,self.parent.buffer[0:self.parent.buffer.index('\n')])
                    self.parent.buffer = self.parent.buffer[self.parent.buffer.index('\n')+1:]
                    if self.parent.DEBUG:
                        sys.stdout.write("DEBUG: Rest of buffer {}\n".format(self.parent.buffer))

    # As described above, SimpleMQTTBoard writes messages to the tcp stream.
    # inner class SimpleMQTTWriter implements abstract class AsipWriter:
    class SimpleMQTTWriter(AsipWriter):
        parent = None

        def __init__(self, parent):
            self.parent = parent

        # val is a string
        # TODO: improve try catch
        def write(self, val):
            # TODO: insert a way to check weather the connection is still open or not
            try:
                # it fills a buffer
                self.parent.buffer = self.parent.buffer + val + '\n'
                if self.parent.DEBUG:
                    sys.stdout.write("DEBUG: Just sent {}".format(val))
            except Exception as e:
                pass

    # ListenerThread and ConsumerThread are implemented following the Producer/Consumer pattern
    # A class for a listener that read the tcp ip messages and put incoming messages on a queue
    # TODO: implement try catch
    class ListenerThread(Thread):

        queue = None
        mqtt_client = None
        running = False
        DEBUG = False
        temp_buff = ""

        # overriding constructor
        def __init__(self, queue, mqtt_client, running, debug, subtopic):
            Thread.__init__(self)
            self.queue = queue
            self.mqtt_client = mqtt_client
            self.mqtt_client.on_message = self.on_message # callback
            self.mqtt_client.subscribe(topic=subtopic)
            self.running = running
            self.DEBUG = debug
            if self.DEBUG:
                sys.stdout.write("DEBUG: listener thread process created \n")

        # if needed, kill will stops the loop inside run method
        def kill(self):
            self.running = False

        # The callback for when a PUBLISH message is received from the server.
        def on_message(self, client, userdata, msg):
            if not msg.payload:
                pass
            else:
                temp = msg.payload.decode('utf-8')
                self.queue.put(temp)
                if self.DEBUG:
                    sys.stdout.write("DEBUG: Received {}\n".format(temp))

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
            while self.running:
                temp = self.queue.get()
                self.asip.process_input(temp)
                self.queue.task_done()

    # ************ END PRIVATE CLASSES *************