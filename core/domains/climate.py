from core.ha_client import call_service
from core.context_manager import context

# ---------------- CONFIGURAÇÃO ----------------

CLIMATE_ROOMS = {
    "quarto": {
        "power_on": "script.gelar_ar_lg_quarto",
        "power_off": "script.desligar_ar_lg_quarto",
        "state": "binary_sensor.ar_condicionado_quarto_contact"
    },
    "closet": {
        "power_on": "script.gelar_ar_lg_closet",
        "power_off": "script.desligar_ar_lg_closet",
        "state": "binary_sensor.sonoff_10017182d6"
    }
}

# ---------------- HANDLER ----------------

def handle(intent: dict):
    action = intent.get("intent")
    search = intent.get("search", "")

    debug = {
        "action": action,
        "search": search,
        "rooms": list(CLIMATE_ROOMS.keys())
    }

    # -------- DESLIGAR AR (INTELIGENTE) --------
    if action == "off" and search == "ar":
        ligados = []

        for room, cfg in CLIMATE_ROOMS.items():
            if is_on(cfg["state"]):
                ligados.append({
                    "room": room,
                    "script": cfg["power_off"]
                })

        if not ligados:
            return {"message": "Nenhum ar-condicionado está ligado."}

        if len(ligados) == 1:
            call_service(
                "script",
                ligados[0]["script"].replace("script.", ""),
                {}
            )
            return {
                "message": f"Ar do {ligados[0]['room']} desligado."
            }

        # mais de um → confirmação
        context.set({
            "domain": "climate",
            "action": "off",
            "candidates": ligados
        })

        nomes = ", ".join(l["room"] for l in ligados)
        return {
            "message": f"Mais de um ar está ligado: {nomes}. Qual deles?"
        }

    # -------- LIGAR AR --------
    if action == "on" and search in CLIMATE_ROOMS:
        script = CLIMATE_ROOMS[search]["power_on"]
    
        call_service(
            "script",
            script.replace("script.", ""),
            {}
        )
    
        return {
            "message": f"Ar do {search} ligado."
        }

    # -------- DESLIGAR AR POR CÔMODO --------
    if action == "off" and search in CLIMATE_ROOMS:
        script = CLIMATE_ROOMS[search]["power_off"]
        call_service("script", script.replace("script.", ""), {})
        return {
            "message": f"Ar do {search} desligado."
        }

    return {
        "message": "Não entendi o comando de ar-condicionado.",
        "debug": debug
    }


# ---------------- CONFIRMAÇÃO ----------------

def handle_confirmation(intent: dict):
    payload = context.data["payload"]
    text = intent.get("text", "").lower()

    debug = {
        "user_text": text,
        "payload": payload
    }

    context.clear()

    # desligar todos
    if "todos" in text:
        for cfg in CLIMATE_ROOMS.values():
            call_service(
                "script",
                cfg["power_off"].replace("script.", ""),
                {}
            )
        return {"message": "Todos os ar-condicionados foram desligados."}

    for c in payload["candidates"]:
        if c["room"] in text:
            call_service(
                "script",
                c["script"].replace("script.", ""),
                {}
            )
            return {"message": f"Ar do {c['room']} desligado."}

    return {
        "message": "Não entendi qual ar desligar.",
        "debug": {
            "intent_text": intent.get("text"),
            "payload": payload
        }
    }

# ---------------- UTIL ----------------

def is_on(entity_id: str) -> bool:
    """
    Consulta simples via HA states (binário)
    """
    from core.ha_client import get_state
    return get_state(entity_id) == "on"
