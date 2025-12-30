import time
from core.ha_client import (
    call_service,
    find_light_entities,
    get_lights_on
)

# ------------------ HANDLER ------------------

def handle(intent: dict):
    intent_type = intent.get("intent")

    # --------- ATALHOS GLOBAIS ---------
    if intent_type in ("all_on", "all_off"):
        return handle_all(intent)

    # --------- MULTI ---------
    if intent_type == "multi":
        return handle_multi(intent)

    # --------- SINGLE ---------
    if "search" in intent:
        return handle_single(intent)

    return {
        "message": "Não entendi o comando."
    }

# ------------------ SINGLE ------------------

def handle_single(intent: dict):
    action = intent.get("intent")
    search = intent.get("search")

    # apagar luz (inteligente)
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

        nomes = [
            e["entity_id"].replace("light.", "").replace("_", " ")
            for e in lights_on
        ]

        return {
            "message": f"Mais de uma luz está ligada: {', '.join(nomes)}. Qual cômodo?"
        }

    # entidade específica
    entities = find_light_entities(search)

    if not entities:
        return {"message": "Não encontrei essa luz."}

    service = "turn_on" if action == "on" else "turn_off"
    call_service("light", service, {"entity_id": entities})

    acao = "ligada" if action == "on" else "desligada"
    return {
        "message": f"{search.capitalize()} {acao}.",
        "entities": entities
    }

# ------------------ MULTI ------------------

def handle_multi(intent: dict):
    """
    Exemplo:
    'apagar luz closet e acender luz jantar'
    """
    text = intent.get("text", "")
    partes = [p.strip() for p in text.split(" e ")]

    respostas = []
    entidades = []

    for parte in partes:
        parte = parte.lower()

        action = "on" if any(a in parte for a in ["ligar", "acender"]) else "off"

        light_type = "luz" if "luz" in parte else "led"

        # remove verbos e tipo → sobra o alvo
        search = parte
        for w in ["ligar", "acender", "desligar", "apagar", "luz", "led"]:
            search = search.replace(w, "")

        search = " ".join(search.split()).strip()
        search = f"{light_type} {search}".strip()

        mini_intent = {
            "intent": action,
            "domain": "light",
            "search": search
        }

        r = handle_single(mini_intent)

        if "entities" in r:
            entidades.extend(r["entities"])

        respostas.append(r.get("message", ""))

        time.sleep(0.5)

    return {
        "message": " | ".join(respostas),
        "entities": list(set(entidades))
    }

# ------------------ ALL ------------------

def handle_all(intent: dict):
    intent_type = intent.get("intent")

    if intent_type == "all_on":
        call_service(
            "light",
            "turn_on",
            {"entity_id": "light.all_light_entities"}
        )
        return {
            "message": "Todas as luzes foram ligadas.",
            "entities": ["light.all_light_entities"]
        }

    if intent_type == "all_off":
        call_service(
            "light",
            "turn_off",
            {"entity_id": "light.all_light_entities"}
        )
        return {
            "message": "Todas as luzes foram desligadas.",
            "entities": ["light.all_light_entities"]
        }

    return {
        "message": "Comando inválido para todas as luzes."
    }
