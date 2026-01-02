import re
import time

from core.context_manager import context
from core.ha_client import call_service, get_all_states
from utils.logger import log_action, setup_logger

logger = setup_logger(__name__)

# ---------------- CONFIG ----------------

IGNORED_LIGHT_ENTITIES = {
    "light.all_light_entities",

    # banheiro
    "light.esp32banheiro_led_banheiro",
    "light.esp32banheiro_led_noturno",
    "light.esp32banheiro_luz_banheiro",
    "light.esp32banheiro_spot_box",

    # quarto / closet
    "light.led_mesa_will",
    "light.esp32ledstrip_zona_bah",
    "light.esp32ledstrip_zona_pe_da_cama",
    "light.esp32ledstrip_zona_will",
    "light.esp32ledstrip_fita_led_quarto",
}

# ---------------- UTIL ----------------

def normalize_name(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(do|da|de)\b", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def get_all_lights():
    return [
        e for e in get_all_states()
        if e["entity_id"].startswith("light.")
    ]

def get_lights_on():
    return [
        e for e in get_all_lights()
        if e["state"] == "on"
        and e["entity_id"] not in IGNORED_LIGHT_ENTITIES
        # descarta grupos (quando existir atributo entity_id)
        and "entity_id" not in e.get("attributes", {})
    ]

def find_light_entities(search: str):
    search = normalize_name(search)
    matches = []

    for e in get_all_lights():
        name = normalize_name(e.get("attributes", {}).get("friendly_name", ""))
        if search in name:
            matches.append(e["entity_id"])

    logger.debug(f"Busca '{search}': {len(matches)} luz(es) encontrada(s)")
    return matches

# ---------------- HANDLER ----------------

def handle(intent: dict):
    intent_type = intent.get("intent")
    logger.info(f"Processando light.{intent_type}")

    if intent_type in ("all_on", "all_off"):
        return handle_all(intent)

    if intent_type == "multi":
        return handle_multi(intent)

    if "search" in intent:
        return handle_single(intent)

    logger.warning(f"Intent desconhecida no dominio light: {intent_type}")
    return {"message": "Não entendi o comando."}

# ---------------- SINGLE ----------------

def handle_single(intent: dict):
    action = intent["intent"]
    search = intent["search"]
    from_multi = intent.get("_from_multi", False)

    # apagar luz genérico
    if action == "off" and search == "luz" and not from_multi:
        lights_on = get_lights_on()

        if not lights_on:
            return {"message": "Nenhuma luz está ligada."}

        if len(lights_on) == 1:
            entity = lights_on[0]["entity_id"]
            call_service("light", "turn_off", {"entity_id": entity})
            log_action(logger, "light", "turn_off", entity)
            return {"message": "Luz desligada."}

        candidates = [
            {
                "entity_id": e["entity_id"],
                "name": e["entity_id"].replace("light.", "").replace("_", " ")
            }
            for e in lights_on
        ]

        logger.info(f"Multiplas luzes ligadas: {len(candidates)} luz(es)")
        context.set({
            "domain": "light",
            "action": "off",
            "candidates": candidates
        })

        nomes = ", ".join(c["name"] for c in candidates)
        return {"message": f"Mais de uma luz está ligada: {nomes}. Qual luz?"}

    entities = find_light_entities(search)
    if not entities:
        logger.warning(f"Luz nao encontrada: '{search}'")
        return {"message": "Não encontrei essa luz."}

    service = "turn_on" if action == "on" else "turn_off"
    call_service("light", service, {"entity_id": entities})
    log_action(logger, "light", service, search)

    return {"message": f"{search} {'ligada' if action == 'on' else 'desligada'}."}

# ---------------- MULTI ----------------

def handle_multi(intent: dict):
    text = intent["text"]
    partes = [p.strip() for p in text.split(" e ")]

    respostas = []

    for parte in partes:
        parte = parte.lower()

        action = "on" if any(v in parte for v in ("ligar", "acender")) else "off"
        light_type = "luz" if "luz" in parte else "led"

        search = parte
        for w in ["ligar", "acender", "desligar", "apagar", "luz", "led"]:
            search = search.replace(w, "")

        search = f"{light_type} {' '.join(search.split())}".strip()

        r = handle_single({
            "intent": action,
            "domain": "light",
            "search": search,
            "_from_multi": True
        })

        respostas.append(r.get("message", ""))
        time.sleep(0.4)

    return {"message": " | ".join(respostas)}

# ---------------- CONFIRMAÇÃO ----------------

def handle_confirmation(intent: dict):
    payload = context.data["payload"]
    user_text = intent.get("text", "").lower()
    context.clear()

    candidates = payload["candidates"]

    if user_text in ("todas", "todas as luzes"):
        call_service("light", "turn_off", {"entity_id": "light.all_light_entities"})
        return {"message": "Todas as luzes foram desligadas."}

    for c in candidates:
        if c["name"] == user_text:
            call_service("light", "turn_off", {"entity_id": c["entity_id"]})
            return {"message": f"{c['name']} desligada."}

    return {"message": "Não encontrei essa luz."}

# ---------------- ALL ----------------

def handle_all(intent: dict):
    service = "turn_on" if intent["intent"] == "all_on" else "turn_off"
    call_service("light", service, {"entity_id": "light.all_light_entities"})
    return {"message": "Comando executado para todas as luzes."}
