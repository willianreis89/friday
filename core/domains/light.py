import time
from core.ha_client import (
    call_service,
    find_light_entities,
    get_lights_on
)

# ---------------- HANDLE ----------------

def handle(intent: dict):

    search = intent.get("search", "").strip()
    action = intent.get("intent")

    # ==================================================
    # 🔥 PRIORIDADE ABSOLUTA → TODAS AS LUZES
    # ==================================================
    if "todas" in search and "luz" in search:
        service = "turn_on" if action == "on" else "turn_off"

        call_service(
            "light",
            service,
            {"entity_id": "light.all_light_entities"}
        )

        return {
            "message": f"Todas as luzes foram {'ligadas' if service == 'turn_on' else 'desligadas'}.",
            "entities": ["light.all_light_entities"]
        }

    # ==================================================
    # 🔥 APAGAR LUZ (AUTO)
    # ==================================================
    if action == "off" and search == "luz":
        lights_on = get_lights_on()

        if not lights_on:
            return {"message": "Nenhuma luz está ligada."}

        if len(lights_on) < 2:
            entity = lights_on[0]["entity_id"]
            call_service("light", "turn_off", {"entity_id": entity})
            return {
                "message": "Luz desligada.",
                "entities": [entity]
            }

        nomes = []
        for l in lights_on:
            nome = l["attributes"].get("friendly_name", "")
            nomes.append(nome)

        lista = ", ".join(nomes)

        return {
            "message": f"Mais de uma luz está ligada: {lista}. Qual cômodo?",
            "entities": [l["entity_id"] for l in lights_on]
        }

    # ==================================================
    # 🔥 SINGLE (luz / led + alvo)
    # ==================================================
    entities = find_light_entities(search)

    if not entities:
        return {"message": "Não encontrei essa luz."}

    service = "turn_on" if action == "on" else "turn_off"

    for e in entities:
        call_service("light", service, {"entity_id": e})
        time.sleep(0.5)  # evita flood no HA

    return {
        "message": f"Luz {'ligada' if service == 'turn_on' else 'desligada'}.",
        "entities": entities
    }
