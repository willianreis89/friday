from core.domains import light

def dispatch(intent: dict):
    if intent.get("domain") == "light":
        return light.handle(intent)

    return {
        "message": "Domínio não suportado."
    }
