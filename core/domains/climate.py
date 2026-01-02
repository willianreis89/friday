from core.ha_client import call_service, get_state
from core.context_manager import context

# ---------------- DEVICES ----------------

CLIMATE_DEVICES = {
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

# ---------------- ALIASES ----------------

GENERIC_AR = {"ar", "ar condicionado", "ar-condicionado", "arcondicionado"}

ROOM_ALIASES = {
    "quarto": ["quarto", "ar quarto", "ar do quarto", "ar condicionado quarto"],
    "closet": ["closet", "ar closet", "ar do closet", "ar condicionado closet"]
}

# ---------------- UTIL ----------------

def match_room(search: str):
    for room, aliases in ROOM_ALIASES.items():
        for a in aliases:
            if a in search:
                return room
    return None

def is_generic_ar(search: str):
    return not search or search in GENERIC_AR

def is_on(entity_id: str):
    return get_state(entity_id) == "on"

# ---------------- HANDLER ----------------

def handle(intent: dict):
    action = intent["intent"]
    search = intent.get("search", "").lower()

    room = match_room(search)

    # GENÉRICO: desligar ar
    if action == "off" and is_generic_ar(search) and not room:
        ligados = [
            {"room": r, "script": cfg["power_off"]}
            for r, cfg in CLIMATE_DEVICES.items()
            if is_on(cfg["state"])
        ]

        if not ligados:
            return {"message": "Nenhum ar-condicionado está ligado."}

        if len(ligados) == 1:
            call_service("script", ligados[0]["script"].replace("script.", ""), {})
            return {"message": f"Ar do {ligados[0]['room']} desligado."}

        context.set({
            "domain": "climate",
            "action": "off",
            "candidates": ligados
        })

        nomes = ", ".join(l["room"] for l in ligados)
        return {"message": f"Mais de um ar está ligado: {nomes}. Qual deles?"}

    # COM CÔMODO
    if room:
        cfg = CLIMATE_DEVICES[room]
        script = cfg["power_on"] if action == "on" else cfg["power_off"]
        call_service("script", script.replace("script.", ""), {})
        return {"message": f"Ar do {room} {'ligado' if action == 'on' else 'desligado'}."}

    return {"message": "Não entendi o comando de ar-condicionado."}

# ---------------- CONFIRMAÇÃO ----------------

def handle_confirmation(intent: dict):
    payload = context.data.get("payload", {})
    text = intent.get("text", "").lower()
    context.clear()

    if payload.get("domain") != "climate":
        return {"message": "Confirmação inválida."}

    candidates = payload.get("candidates", [])

    if "todos" in text:
        for c in candidates:
            call_service("script", c["script"].replace("script.", ""), {})
        return {"message": "Todos os ar-condicionados foram desligados."}

    for c in candidates:
        if c["room"] in text:
            call_service("script", c["script"].replace("script.", ""), {})
            return {"message": f"Ar do {c['room']} desligado."}

    return {"message": "Não entendi qual ar desligar."}
