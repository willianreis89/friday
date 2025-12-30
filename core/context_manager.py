import time

class ContextManager:
    def __init__(self):
        self.data = None

    def set(self, payload: dict, ttl=20):
        self.data = {
            "payload": payload,
            "expires": time.time() + ttl
        }

    def clear(self):
        self.data = None

    def valid(self):
        return self.data and time.time() < self.data["expires"]

    def handle(self, intent):
        if not self.valid():
            return "Não há nada para confirmar."

        if intent["intent"] == "deny":
            self.clear()
            return "Ok, cancelado."

        return "Certo."

context = ContextManager()
