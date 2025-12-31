import time

class ContextManager:
    def __init__(self):
        self.data = None

    def set(self, payload: dict, ttl=10):
        self.data = {
            "payload": payload,
            "expires": time.time() + ttl
        }

    def clear(self):
        self.data = None

    def valid(self):
        return self.data and time.time() < self.data["expires"]

context = ContextManager()
