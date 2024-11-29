import json
from actuator_emulator import Actuator

class ActuatorService:
    def __init__(self, mqtt_client, actuators_config):
        self.mqtt_client = mqtt_client
        self.actuators = self.load_actuators(actuators_config)

    def load_actuators(self, actuators_config):
        actuators = []
        for actuator_config in actuators_config:
            actuators.append(Actuator(
                name=actuator_config["name"],
                actuator_type=actuator_config["type"],
                mqtt_client=self.mqtt_client
            ))
        return actuators
