import re
import unicodedata

# ------------------ NORMALIZACAO ------------------

STOPWORDS = {
    "do", "da", "de", "dos", "das",
    "no", "na", "nos", "nas",
    "para", "pra", "pro",
    "pelo", "pela"
}

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)\
        .encode("ascii", "ignore")\
        .decode("ascii")\
        .lower()

    words = text.split()
    words = [w for w in words if w not in STOPWORDS]

    return " ".join(words)

# ------------------ VOCABULARIO ------------------

ACTIONS_ON = ["ligar", "acender"]
ACTIONS_OFF = ["desligar", "apagar"]

LIGHT_TYPES = ["luz", "led"]

# ------------------ PARSER ------------------

def parse(text: str):
    raw = normalize(text)

    # ação
    if any(a in raw for a in ACTIONS_ON):
        action = "on"
    elif any(a in raw for a in ACTIONS_OFF):
        action = "off"
    else:
        return {
            "intent": "error",
            "domain": "light",
            "response": "Não entendi."
        }

    # tipo
    light_type = None
    for t in LIGHT_TYPES:
        if t in raw:
            light_type = t
            break

    if not light_type:
        return {
            "intent": "error",
            "domain": "light",
            "response": "Voce quer controlar luz ou led?"
        }

    # remove ação e tipo → sobra só o alvo (friendly)
    target = raw
    for w in ACTIONS_ON + ACTIONS_OFF + LIGHT_TYPES:
        target = target.replace(w, "")

    target = " ".join(target.split()).strip()

    return {
        "intent": action,
        "domain": "light",
        "type": light_type,
        "search": f"{light_type} {target}".strip()
    }


