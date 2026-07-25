class EventManager:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_name, callback):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def unsubscribe(self, event_name, callback):
        if event_name in self.listeners:
            self.listeners[event_name].remove(callback)

    def emit(self, event_name, data=None):
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in listener for {event_name}: {e}")
