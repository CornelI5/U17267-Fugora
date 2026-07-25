import time
import requests


class DataSource:
    def __init__(self, name):
        self.name = name
        self.active = False
        self.last_update = 0

    def connect(self):
        self.active = True

    def disconnect(self):
        self.active = False

    def fetch_data(self):
        raise NotImplementedError


class NasaNeoSource(DataSource):
    def __init__(self, api_key="DEMO_KEY"):
        super().__init__("NASA_NEO")
        self.api_key = api_key
        self.base_url = "https://api.nasa.gov/neo/rest/v1/feed"

    def fetch_data(self):
        if not self.active:
            return None

        today = time.strftime("%Y-%m-%d", time.gmtime())
        params = {
            "start_date": today,
            "end_date": today,
            "api_key": self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.last_update = time.time()
            return data
        except Exception as e:
            print(f"Error fetching NASA data: {e}")
            return None


class SourceManager:
    def __init__(self, allow_external=False):
        self.sources = {}
        self.allow_external = allow_external

    def add_source(self, source):
        self.sources[source.name] = source

    def get_all_data(self):
        if not self.allow_external:
            return {}
            
        data = {}
        for name, source in self.sources.items():
            if source.active:
                result = source.fetch_data()
                if result:
                    data[name] = result
        return data

    def activate_all(self):
        for source in self.sources.values():
            source.connect()

    def deactivate_all(self):
        for source in self.sources.values():
            source.disconnect()
