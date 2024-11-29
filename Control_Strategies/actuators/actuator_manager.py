import json

class ActuatorManager:
    def __init__(self, catalog_file, raspberry_id):
        self.catalog_file = catalog_file
        self.raspberry_id = raspberry_id
        self.actuators = self._load_actuators()

    def _load_actuators(self):
        with open(self.catalog_file) as f:
            catalog = json.load(f)

        for client in catalog["clients"]:
            if client["raspberry_id"] == self.raspberry_id:
                return client["metrics"]

        raise ValueError(f"Raspberry Pi {self.raspberry_id} non trovato nel catalogo.")

    def get_actuators(self, metric):
        return self.actuators.get(metric, {}).get("actuators", [])
