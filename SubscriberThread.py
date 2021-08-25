import paho.mqtt.client as mqtt

from led_thread import LedThread
from log_thread import LogThread

import socket

class SubscriberThread(LogThread):

    def __init__(self, mac_master, own_mac, face_id, BROKER_IP):
        own_mac = own_mac.upper()
        LogThread.__init__(self, "MQTT {}".format(own_mac))
        # init MQTT as slave
        self.client = mqtt.Client(client_id=own_mac)
        self.client.username_pw_set(username="slave", password="slave")

        # start socket towards c++ code
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect(('localhost', 6666))
        self.log("Connected to socket")

        # connect to MQTT
        self.client.connect(BROKER_IP, 1884, 60)
        self.client.on_connect = self.on_connect
        # pair to master
        topic = "directions/effector/pair/{}".format(mac_master.lower())
        self.log("PAIRING ON TOPIC {}".format(topic))
        payload = "{}${}".format(own_mac, face_id)
        self.client.publish(topic, payload)


    def on_connect(self, client, userdata, flags, rc):
        self.log("CONNECTED")
        self.client.subscribe("#")
        self.client.message_callback_add('directions/slave/activate/#', self.show_direction)

    def show_direction(self, client, userdata, msg):
        self.log("SHOW DIRECTION")
        relative_msg_to_show, color, execution_time = msg.payload.decode('utf-8').split("$")
        LedThread("", color, relative_msg_to_show, execution_time, self.connection).start()

    def run(self):
        self.client.loop_forever()

