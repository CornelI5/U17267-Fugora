import time


class DataSource:
    def __init__(self, name):
        self.name = name
        self.active = False
        self.last_update = 0

    def connect(self):
        self.active = True
        print(f"Connected to source: {self.name}")

    def disconnect(self):
        self.active = False
        print(f"Disconnected from source: {self.name}")

    def fetch_data(self):
        raise NotImplementedError


class DummySatelliteSource(DataSource):
    def __init__(self):
        super().__init__("DummySatellite")

    def fetch_data(self):
        if not self.active:
            return None
        
        self.last_update = time.time()
        # Simulasi data telemetry palsu
        return {
            "timestamp": self.last_update,
            "object_id": "U17267",
            "position_noise": [0.0, 0.0, 0.0], # Nanti bisa diisi noise beneran
            "status": "OK"
        }


class SourceManager:
    def __init__(self):
        self.sources = {}

    def add_source(self, source):
        self.sources[source.name] = source

    def get_all_data(self):
        data = {}
        for name, source in self.sources.items():
            if source.active:
                data[name] = source.fetch_data()
        return data

    def activate_all(self):
        for source in self.sources.values():
            source.connect()

    def deactivate_all(self):
        for source in self.sources.values():
            source.disconnect()
