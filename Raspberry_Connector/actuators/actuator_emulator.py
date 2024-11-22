import json
import paho.mqtt.client as mqtt

class ActuatorService:
    def __init__(self, broker_ip, broker_port, metric_name, actuator_type):
        self.metric_name = metric_name
        self.actuator_type = actuator_type
        self.client = mqtt.Client(f"{metric_name}_{actuator_type}_Actuator")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker_ip, broker_port)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        topic = f"GreenBox/actuators/{self.metric_name}/{self.actuator_type}"
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload)
        activate = data.get("activate")
        if activate:
            self.activate()
        else:
            self.deactivate()

    def activate(self):
        print(f"{self.actuator_type.capitalize()} actuator for {self.metric_name} activated.")

    def deactivate(self):
        print(f"{self.actuator_type.capitalize()} actuator for {self.metric_name} deactivated.")

if __name__ == "__main__":
    # Esempio: Attuatore di riscaldamento per la temperatura
    heating_actuator = ActuatorService(
        broker_ip="mqtt.eclipseprojects.io",
        broker_port=1883,
        metric_name="temperature",
        actuator_type="heating"
    )

    # Esempio: Attuatore di raffreddamento per la temperatura
    cooling_actuator = ActuatorService(
        broker_ip="mqtt.eclipseprojects.io",
        broker_port=1883,
        metric_name="temperature",
        actuator_type="cooling"
    )

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Actuator service stopped.")
