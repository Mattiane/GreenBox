import time
from control_module import ControlModule
from tools.my_mqtt import MyMQTT
import json

# Configuration
#BROKER_IP = "localhost"
   # BROKER_PORT = 1883

    # Define identifiers
    #client_id = "01f20b9e-6df4-43df-9fd6-c1376bb2ba41"
    #greenhouse_id = "greenhouse1"
    #raspberry_id = "rb01"  # Specific Raspberry Pi identifier
    #sensor_id = "dht11"
    #measurement_type = "temperature"

    # Construct the base topic dynamically
    #base_topic = f"/{client_id}/{greenhouse_id}/{raspberry_id}/{sensor_id}/{measurement_type}"


# Percorsi file di configurazione
CONFIG_FILE = "config.json"
CATALOG_FILE = "catalog.json"

def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    # Carica configurazioni e catalogo
    config = load_config(CONFIG_FILE)
    catalog = load_config(CATALOG_FILE)

    broker_ip = config["ip"]
    broker_port = config["port"]

    # Base topic per le metriche
    base_topic_template = "/{client_id}/{greenhouse_id}/{raspberry_id}/{sensor_id}/{metric}/statistics"

    # Configura i client MQTT per ogni metrica nel catalogo
    mqtt_clients = []
    for client in catalog["clients"]:
        client_name = client["client_name"]
        raspberry_id = client["raspberry_id"]
        strategy_name = client["control_strategy"]

        # Inizializza modulo di controllo
        control_module = ControlModule(raspberry_id, strategy_name)

        # Crea un client MQTT per ogni metrica
        for metric in ["temperature", "air_humidity", "soil_humidity", "par_level", "ph_level"]:  # Estendi con nuove metriche in futuro
            sensor_id = f"{metric}_sensor"  # ID del sensore basato sulla metrica
            topic = base_topic_template.format(
                client_id=client_name,
                greenhouse_id="default_greenhouse",
                raspberry_id=raspberry_id,
                sensor_id=sensor_id,
                metric=metric
            )

            # Configura il client MQTT
            client_id = f"{raspberry_id}_{metric}_Client"
            mqtt_client = MyMQTT(client_id, broker_ip, broker_port)
            mqtt_client.set_control_module(control_module)
            mqtt_client.start()
            mqtt_client.mySubscribe(topic)

            print(f"[INFO] MQTT client configured for {metric} on topic {topic}")

            # Aggiungi il client alla lista
            mqtt_clients.append(mqtt_client)

    # Mantieni il servizio in esecuzione
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("[INFO] Shutting down MQTT clients...")
        for client in mqtt_clients:
            client.stop()
