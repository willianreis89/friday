from core.domains import light, climate
from core.context_manager import context

def dispatch(intent: dict):
    """
    Ordem correta:
    1) Confirmação contextual (se existir e domínio bater)
    2) Domínio normal
    3) Fallback
    """

    # ---------- CONFIRMAÇÃO CONTEXTUAL ----------
    if context.valid():
        payload = context.data.get("payload", {})
        payload_domain = payload.get("domain")
        intent_domain = intent.get("domain")

        # só confirma se o domínio bater
        if payload_domain and payload_domain == intent_domain:
            if payload_domain == "light":
                return light.handle_confirmation(intent)

            if payload_domain == "climate":
                return climate.handle_confirmation(intent)

        # se não bateu domínio, IGNORA confirmação
        # (não limpa contexto ainda, deixa expirar por TTL)

    # ---------- DOMÍNIOS ----------
    if intent.get("domain") == "light":
        return light.handle(intent)

    if intent.get("domain") == "climate":
        return climate.handle(intent)

    # ---------- FALLBACK ----------
    return intent.get(
        "response",
        {"message": "Não entendi. Você poderia repetir?"}
    )
