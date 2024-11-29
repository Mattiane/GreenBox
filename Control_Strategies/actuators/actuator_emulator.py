import json

class Actuator:
    def __init__(self, name, actuator_type, mqtt_client):
        self.name = name
        self.type = actuator_type
        self.mqtt_client = mqtt_client

    def notify(self, topic, message):
        data = json.loads(message)
        activate = data.get("activate")
        if activate:
            self.activate()
        else:
            self.deactivate()

    def activate(self):
        print(f"[INFO] {self.name} ({self.type}) activated.")

    def deactivate(self):
        print(f"[INFO] {self.name} ({self.type}) deactivated.")
