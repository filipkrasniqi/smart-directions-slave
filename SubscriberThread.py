import paho.mqtt.client as mqtt

from led_thread import LedThread
from log_thread import LogThread

class SubscriberThread(LogThread):

    def __init__(self, mac_master, own_mac, face_id, BROKER_IP):
        own_mac = own_mac.upper()
        LogThread.__init__(self, "MQTT")
        self.client = mqtt.Client(client_id=own_mac)
        self.client.username_pw_set(username="slave", password="slave")
        #print(own_mac)
        #print(BROKER_IP)
        self.client.connect(BROKER_IP, 1884, 60)
        self.client.on_connect = self.on_connect
        topic = "directions/effector/pair/{}".format(mac_master)
        payload = "{}${}".format(own_mac, face_id)
        #print(topic)
        #print(payload)
        self.client.publish(topic,payload)

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("#")
        self.client.message_callback_add('directions/slave/activate/#', self.show_direction)

    def show_direction(self, client, userdata, msg):
        relative_msg_to_show = msg.payload.decode('utf-8')
        LedThread("", relative_msg_to_show).start()

    def run(self):
        self.client.loop_forever()

