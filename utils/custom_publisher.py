import logging
import json

import paho.mqtt.client as mqtt


class CustomPublisher:
    def __init__(self, client_id, topic, broker='mqtt.eclipseprojects.io', port=1883):
        self.client_id = client_id
        self.topic = topic
        self.broker = broker
        self.port = port

        # client initialization
        self._mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id, clean_session=False)
        # registering callbacks
        self._mqtt.on_connect = self.on_connect

    def start(self):
        self._mqtt.connect(self.broker, self.port)
        self._mqtt.loop_start()

    def stop(self):
        self._mqtt.loop_stop()
        self._mqtt.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        logging.debug('Connected to the broker with result code: %d' % rc)

    def publish(self, message, qos=2):
        logging.debug('Client "%s" published message on topic "%s": "%s"' % (self.client_id, self.topic, message))
        self._mqtt.publish(self.topic, json.dumps(message), qos)
