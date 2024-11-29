import logging

logger = logging.getLogger("GreenBox")

class ControlStrategy:
    def __init__(self, thresholds, actuators, mqtt_client, base_topic):
        """
        Classe base per implementare strategie di controllo.
        """
        self.thresholds = thresholds
        self.actuators = actuators
        self.mqtt_client = mqtt_client
        self.base_topic = base_topic

    def analyze_statistics(self, statistics):
        """
        Analizza le statistiche e applica la strategia di controllo.
        """
        metric_value = statistics.get("mean_temperature")
        std_dev = statistics.get("std_dev", 0)
        print(f"[DEBUG] Metric value: {metric_value}, Std Dev: {std_dev}")

        if metric_value < self.thresholds["min"]:
            print("[INFO] Metric is below minimum threshold. No action taken.")
        elif self.thresholds["min"] <= metric_value <= self.thresholds["max"]:
            print("[INFO] Metric is within thresholds. Applying base strategy.")
            self.apply_base_strategy()
        else:
            print("[INFO] Metric is above maximum threshold.")
            if std_dev > 5:  # Arbitrary value for std_dev
                print("[INFO] High standard deviation detected. Applying advanced strategy.")
                self.apply_advanced_strategy()
            else:
                print("[INFO] Standard deviation is normal. Applying base strategy.")
                self.apply_base_strategy()

    def apply_base_strategy(self):
        """
        Strategia base: accende solo il primo attuatore.
        """
        for actuator in self.actuators[:1]:  # Solo il primo attuatore
            self.send_command(actuator, "on")

    def apply_advanced_strategy(self):
        """
        Strategia avanzata: accende tutti gli attuatori.
        """
        for actuator in self.actuators:
            self.send_command(actuator, "on")

    def send_command(self, actuator, command):
        """
        Invia un comando a un attuatore.
        """
        topic = f"{self.base_topic}/actuators/{actuator['name']}"
        payload = {"command": command, "name": actuator["name"]}
        self.mqtt_client.myPublish(topic, payload)
        print(f"[DEBUG] Command '{command}' sent to {actuator['name']} on topic {topic}")


class BasicTemperatureControlStrategy(ControlStrategy):
    """
    Strategia per il controllo della temperatura.
    """
    def analyze_statistics(self, statistics,topic):
        print(f"[DEBUG] Analyzing temperature statistics from topic {topic}: {statistics}")
        print(f"[DEBUG] Analyzing temperature statistics: {statistics}")
        temp = statistics.get("mean_temperature")
        std_dev = statistics.get("std_dev", 0)

        if temp < self.thresholds["min"]:
            print("[INFO] Temperature below minimum threshold. No action needed.")
        elif self.thresholds["min"] <= temp <= self.thresholds["max"]:
            print("[INFO] Temperature within thresholds. Applying base strategy.")
            self.apply_base_strategy()
        elif temp > self.thresholds["max"] and std_dev > 5:
            print("[INFO] Temperature above threshold with high standard deviation. Applying advanced strategy.")
            self.apply_advanced_strategy()
        else:
            print("[INFO] Temperature above threshold but standard deviation is normal. Applying base strategy.")
            self.apply_base_strategy()


class BasicHumidityControlStrategy(ControlStrategy):
    """
    Strategia per il controllo dell'umidità.
    """
    def analyze_statistics(self, statistics,topic):
        print(f"[DEBUG] Analyzing humidity statistics from topic {topic}: {statistics}")
        print(f"[DEBUG] Analyzing humidity statistics: {statistics}")
        humidity = statistics.get("mean_humidity")
        std_dev = statistics.get("std_dev", 0)

        if humidity < self.thresholds["min"]:
            print("[INFO] Humidity below minimum threshold. No action needed.")
        elif self.thresholds["min"] <= humidity <= self.thresholds["max"]:
            print("[INFO] Humidity within thresholds. Applying base strategy.")
            self.apply_base_strategy()
        elif humidity > self.thresholds["max"] and std_dev > 5:
            print("[INFO] Humidity above threshold with high standard deviation. Applying advanced strategy.")
            self.apply_advanced_strategy()
        else:
            print("[INFO] Humidity above threshold but standard deviation is normal. Applying base strategy.")
            self.apply_base_strategy()

class SoilHumidityControlStrategy(ControlStrategy):
    def analyze_statistics(self, statistics, topic):
        logger.debug(f"Analyzing soil humidity statistics from topic {topic}: {statistics}")
        humidity = statistics.get("mean_soil_humidity")
        if humidity is None:
            logger.error("Missing 'mean_humidity' in statistics. Skipping analysis.")
            return
        if humidity < self.thresholds["min"]:
            logger.info("Soil humidity below minimum threshold. Activating irrigation.")
            self.apply_base_strategy()
        elif humidity > self.thresholds["max"]:
            logger.info("Soil humidity above maximum threshold. No action needed.")
        else:
            logger.info("Soil humidity within thresholds. No action needed.")

class ParMeterControlStrategy(ControlStrategy):
    def analyze_statistics(self, statistics, topic):
        logger.debug(f"Analyzing PAR meter statistics from topic {topic}: {statistics}")
        par_value = statistics.get("mean_par_value")
        if par_value is None:
            logger.error("Missing 'mean_par_value' in statistics. Skipping analysis.")
            return
        if par_value < self.thresholds["min"]:
            logger.info("PAR value below minimum threshold. Activating lighting system.")
            self.apply_base_strategy()
        elif par_value > self.thresholds["max"]:
            logger.info("PAR value above maximum threshold. Deactivating lighting system.")
            self.apply_advanced_strategy()

class PHControlStrategy(ControlStrategy):
    def analyze_statistics(self, statistics, topic):
        logger.debug(f"Analyzing pH statistics from topic {topic}: {statistics}")
        ph_value = statistics.get("mean_pH")
        if ph_value is None:
            logger.error("Missing 'mean_pH' in statistics. Skipping analysis.")
            return
        if ph_value < self.thresholds["min"]:
            logger.info("pH below minimum threshold. Adjusting pH up.")
            self.apply_base_strategy()
        elif ph_value > self.thresholds["max"]:
            logger.info("pH above maximum threshold. Adjusting pH down.")
            self.apply_advanced_strategy()
