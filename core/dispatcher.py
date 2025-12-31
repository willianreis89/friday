from core.domains import light
from core.context_manager import context

def dispatch(intent: dict):
    """
    Ordem correta:
    1) Confirmação contextual (se existir)
    2) Domínio light
    3) Fallback
    """

    # ---------- CONFIRMAÇÃO CONTEXTUAL ----------
    if (
        context.valid()
        and "search" not in intent              # não é single normal
        and intent.get("intent") not in (
            "multi",
            "all_on",
            "all_off"
        )
    ):
        return light.handle_confirmation(intent)

    # ---------- LUZ ----------
    if intent.get("domain") == "light":
        return light.handle(intent)

    # ---------- FALLBACK ----------
    return intent.get(
        "response",
        {"message": "Não entendi. Você poderia repetir?"}
    )
