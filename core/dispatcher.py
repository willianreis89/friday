from core.domains import light
from core.context_manager import context

def dispatch(intent: dict):
    domain = intent.get("domain")

    # ---------------- CONTEXTO ----------------
    # Ex: "sim", "não", confirmações
    if domain == "context":
        return context.handle(intent)

    # ---------------- LUZ ----------------
    if domain == "light":
        return light.handle(intent)

    # ---------------- FALLBACK ----------------
    return intent.get("response", "Não entendi.")
