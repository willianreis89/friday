from core.domains import light, climate
from core.context_manager import context

def dispatch(intent: dict):
    if context.valid():
        payload = context.data.get("payload", {})
        domain = payload.get("domain")

        if domain == "light":
            return light.handle_confirmation(intent)
        if domain == "climate":
            return climate.handle_confirmation(intent)

    if intent.get("domain") == "light":
        return light.handle(intent)

    if intent.get("domain") == "climate":
        return climate.handle(intent)

    return {"message": "Não entendi. Pode repetir?"}
