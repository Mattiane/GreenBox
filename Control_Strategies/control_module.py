
from actuators.actuator_manager import ActuatorManager

from control_strategies import ControlStrategyFactory


class ControlModule:
    def __init__(self, mqtt_client, raspberry_id, base_topic, catalog_file):
        self.mqtt_client = mqtt_client
        self.base_topic = base_topic
        self.raspberry_id = raspberry_id
        self.actuator_manager = ActuatorManager(catalog_file, raspberry_id)

    def analyze_statistics(self, statistics, metric):
        print(f"[DEBUG] Analyzing statistics for {metric}: {statistics}")
        actuators = self.actuator_manager.get_actuators(metric)
        print(f"[DEBUG] Found actuators for {metric}: {actuators}")
        if not actuators:
            print("[ERROR] No actuators found for metric")
        thresholds = actuators.get("thresholds", {})
        strategy_name = actuators.get("control_strategy", "BasicTemperatureControlStrategy")
        print(f"[DEBUG] Using strategy: {strategy_name}")
        strategy = ControlStrategyFactory.create(strategy_name, thresholds, self.mqtt_client, self.base_topic, actuators)
        strategy.analyze_statistics(statistics)





