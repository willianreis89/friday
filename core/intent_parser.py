import unicodedata

from utils.logger import setup_logger

logger = setup_logger(__name__)

# ------------------ NORMALIZAÇÃO ------------------

STOPWORDS = {
    "do", "da", "de", "dos", "das",
    "no", "na", "nos", "nas",
    "para", "pra", "pro",
    "pelo", "pela",
    # artigos e pronomes comuns em PT-BR
    "a", "o", "as", "os", "um", "uma", "uns", "umas"
}

def normalize(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKD", text)\
        .encode("ascii", "ignore")\
        .decode("ascii")\
        .lower()

    words = [w for w in text.split() if w not in STOPWORDS]
    normalized = " ".join(words)
    logger.debug(f"Normalizado: '{text}' -> '{normalized}'")
    return normalized

# ------------------ VOCABULÁRIO ------------------

ACTIONS_ON = ["ligar", "acender"]
ACTIONS_OFF = ["desligar", "apagar"]
LIGHT_TYPES = ["luz", "led"]
CLIMATE_TYPES = ["ar", "ar condicionado", "ar-condicionado"]

# ------------------ PARSER ------------------

def parse(text: str):
    raw = normalize(text)

    # ------------------ CLIMATE ------------------    
    words = raw.split()
    
    if "ar" in words or "ar-condicionado" in raw or "ar condicionado" in raw:
        if any(a in words for a in ACTIONS_ON):
            action = "on"
        elif any(a in words for a in ACTIONS_OFF):
            action = "off"
        else:
            return {
                "intent": "error",
                "domain": "climate",
                "response": "Você quer ligar ou desligar o ar?",
                "text": text
            }
    
        # remove palavras de ação e tipo, mantendo somente o cômodo
        blacklist = set(ACTIONS_ON + ACTIONS_OFF + ["ar", "condicionado"])
        target_words = [w for w in words if w not in blacklist]
    
        search = " ".join(target_words)
    
        return {
            "intent": action,
            "domain": "climate",
            "search": search if search else "ar",
            "text": text
        }

    # ------------------ TODAS AS LUZES ------------------
    if "todas" in raw and ("luz" in raw or "luzes" in raw):
        if any(a in words for a in ACTIONS_ON):
            return {
                "intent": "all_on",
                "domain": "light",
                "entities": ["light.all_light_entities"],
                "text": text
            }
        if any(a in words for a in ACTIONS_OFF):
            return {
                "intent": "all_off",
                "domain": "light",
                "entities": ["light.all_light_entities"],
                "text": text
            }

    # ------------------ MULTI ------------------
    actions_found = []
    for a in ACTIONS_ON:
        if a in words:
            actions_found.append("on")
    for a in ACTIONS_OFF:
        if a in words:
            actions_found.append("off")

    if (
        len(actions_found) > 1
        and any(t in raw for t in LIGHT_TYPES)
    ) or (" e " in raw and any(a in words for a in ACTIONS_ON + ACTIONS_OFF)):
        return {
            "intent": "multi",
            "domain": "light",
            "text": text
        }

    # ------------------ SINGLE ------------------
    if any(a in words for a in ACTIONS_ON):
        action = "on"
    elif any(a in words for a in ACTIONS_OFF):
        action = "off"
    else:
        return {
            "intent": "error",
            "domain": "light",
            "response": "Não entendi.",
            "text": text
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
            "response": "Você quer controlar luz ou led?",
            "text": text
        }

    target = raw
    for w in ACTIONS_ON + ACTIONS_OFF + LIGHT_TYPES:
        target = target.replace(w, "")

    target = " ".join(target.split()).strip()

    return {
        "intent": action,
        "domain": "light",
        "type": light_type,
        "search": f"{light_type} {target}".strip(),
        "text": text
    }
