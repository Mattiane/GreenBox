import json
import logging
from tools.my_mqtt import MyMQTT
import control_strategies  # Importa il modulo con tutte le strategie

# Configurazione del logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("GreenBox")

def load_catalog(file_path):
    """
    Carica il catalogo delle strategie e degli attuatori.
    """
    with open(file_path, "r") as f:
        return json.load(f)

def notify_factory(strategy):
    """
    Factory per creare un callback di notifica per una strategia specifica.
    """
    def notify(topic, message):
        logger.debug(f"Message received on topic: {topic}")
        try:
            statistics = json.loads(message)
            logger.debug(f"Sending statistics to control module: {statistics}")
            strategy.analyze_statistics(statistics, topic)  # Passa il topic specifico
        except json.JSONDecodeError as e:
            logger.error(f"Failed to process message: {e}")
            logger.error(f"Invalid message received: {message}")
    return notify


if __name__ == "__main__":
    logger.info("Starting GreenBox Control Service")

    # Carica il catalogo
    catalog = load_catalog("Control_Strategies/catalog_controls.json")

    mqtt_client = MyMQTT("ControlService", "localhost", 1883)
    mqtt_client.start()

    try:
        # Cicla su tutti i client nel catalogo
        for client in catalog["clients"]:
            raspberry_id = client["raspberry_id"]
            base_topic = f"/{raspberry_id}"

            for metric, config in client["metrics"].items():
                # Sottoscrivi al topic della metrica
                topic = f"{base_topic}/{metric}/statistics"
                mqtt_client.mySubscribe(topic)
                logger.info(f"Subscribed to {topic}")

                # Carica la classe della strategia dinamicamente
                strategy_class_name = config["control_strategy"]
                try:
                    strategy_class = getattr(control_strategies, strategy_class_name)
                except AttributeError:
                    raise ImportError(f"Strategy class {strategy_class_name} not found in control_strategies module")

                # Crea la strategia
                strategy = strategy_class(
                    thresholds=config["thresholds"],
                    actuators=config["actuators"],
                    mqtt_client=mqtt_client,
                    base_topic=base_topic
                )

                # Associa la strategia al client MQTT
                notifier = notify_factory(strategy)
                mqtt_client.set_control_module(strategy)
                mqtt_client.notifier = notify_factory(strategy)

        logger.info("Control Service running")
        while True:
            pass
    except KeyboardInterrupt:
        mqtt_client.stop()
        logger.info("Stopping GreenBox Control Service")
