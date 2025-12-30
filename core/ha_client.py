import os
import requests
import re
import unicodedata

HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# entidades que NAO devem ser consideradas como "luz principal"
IGNORED_LIGHT_ENTITIES = {
    "light.all_light_entities",

    # banheiro
    "light.esp32banheiro_led_banheiro",
    "light.esp32banheiro_led_noturno",
    "light.esp32banheiro_luz_banheiro",
    "light.esp32banheiro_spot_box",

    # closet / quarto
    "light.led_mesa_will",
    "light.esp32ledstrip_zona_bah",
    "light.esp32ledstrip_zona_pe_da_cama",
    "light.esp32ledstrip_zona_will",
    "light.esp32ledstrip_fita_led_quarto",

    # outros
    "light.esp323dprinter_luzes",
}


# ---------------- CORE CALL ----------------

def call_service(domain, service, data):
    url = f"{HA_URL}/api/services/{domain}/{service}"
    r = requests.post(url, headers=HEADERS, json=data, timeout=5)
    r.raise_for_status()
    return True

# ---------------- STATES ----------------

def get_all_lights():
    url = f"{HA_URL}/api/states"
    r = requests.get(url, headers=HEADERS, timeout=5)
    r.raise_for_status()
    return [e for e in r.json() if e["entity_id"].startswith("light.")]

def get_lights_on():
    lights = get_all_lights()

    return [
        e for e in lights
        if e["state"] == "on"
        # descarta grupos de luz
        and "entity_id" not in e.get("attributes", {})
        # descarta helpers globais
        and e["entity_id"] not in IGNORED_LIGHT_ENTITIES
    ]

# ---------------- SEARCH ----------------

def normalize_name(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(do|da|de)\b", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def find_light_entities(search_text: str):
    search_text = normalize_name(search_text)

    matches = []
    for e in get_all_lights():
        name = normalize_name(e.get("attributes", {}).get("friendly_name", ""))
        if search_text in name:
            matches.append(e["entity_id"])

    return matches

