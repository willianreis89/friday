import re
import unicodedata

# ------------------ NORMALIZAÇÃO ------------------

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

    words = [w for w in text.split() if w not in STOPWORDS]
    return " ".join(words)

# ------------------ VOCABULÁRIO ------------------

ACTIONS_ON = ["ligar", "acender"]
ACTIONS_OFF = ["desligar", "apagar"]
LIGHT_TYPES = ["luz", "led"]

# ------------------ PARSER ------------------

def parse(text: str):
    raw = normalize(text)

    # ------------------ TODAS AS LUZES (ATALHO GLOBAL) ------------------
    if "todas" in raw and ("luz" in raw or "luzes" in raw):
        if any(a in raw for a in ACTIONS_ON):
            return {
                "intent": "all_on",
                "domain": "light",
                "entities": ["light.all_light_entities"]
            }

        if any(a in raw for a in ACTIONS_OFF):
            return {
                "intent": "all_off",
                "domain": "light",
                "entities": ["light.all_light_entities"]
            }
    actions_found = []
    for a in ACTIONS_ON:
        if a in raw:
            actions_found.append("on")
    for a in ACTIONS_OFF:
        if a in raw:
            actions_found.append("off")

    # 🔒 GATE DO MULTI
    if (
        len(actions_found) > 1
        and any(t in raw for t in LIGHT_TYPES)
    ):
        return {
            "intent": "multi",
            "domain": "light",
            "text": raw
        }

    # ---------- SINGLE (como já estava funcionando) ----------

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

    light_type = None
    for t in LIGHT_TYPES:
        if t in raw:
            light_type = t
            break

    if not light_type:
        return {
            "intent": "error",
            "domain": "light",
            "response": "Você quer controlar luz ou led?"
        }

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
