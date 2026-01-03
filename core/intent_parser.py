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

def extract_number(text: str) -> int | None:
    """Extrai o primeiro número encontrado no texto."""
    import re
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None

def extract_temperature_range(text: str) -> tuple[int, int] | None:
    """Extrai range de temperatura (ex: '18-26' retorna (18, 26))."""
    import re
    match = re.search(r'(\d+)\s*-\s*(\d+)', text)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return None

def extract_room_from_climate(raw: str, text_lower: str) -> str | None:
    """Extrai cômodo da busca de climate (quarto, closet, etc)."""
    if "quarto" in raw or "quarto" in text_lower:
        return "quarto"
    if "closet" in raw or "closet" in text_lower:
        return "closet"
    return None

# ------------------ VOCABULÁRIO ------------------

ACTIONS_ON = ["ligar", "acender"]
ACTIONS_OFF = ["desligar", "apagar"]
LIGHT_TYPES = ["luz", "led"]
CLIMATE_TYPES = ["ar", "ar condicionado", "ar-condicionado"]

# Climate sub-features (ventilador, aquecedor, temperatura, velocidade, tela)
CLIMATE_FEATURES = {
    "fan": ["ventilador", "fan"],
    "heater": ["aquecedor", "aquecimento"],
    "temperature": ["temperatura", "graus"],
    "speed": ["velocidade", "speed"],
    "display": ["tela", "display", "scoreboard"]
}

# ------------------ PARSER ------------------

def parse(text: str):
    raw = normalize(text)

    # ---- VERIFICA FEATURES DE CLIMATE (antes de checar por "ar")
    text_lower = text.lower()
    
    # Checagem rápida: se tem algum feature de climate, trata como climate
    has_climate_feature = any(
        any(feat in text_lower for feat in CLIMATE_FEATURES[feature])
        for feature in CLIMATE_FEATURES
    )
    
    # ---- CLIMATE (com features ou com "ar")
    words = raw.split()
    
    if has_climate_feature or "ar" in words or "ar-condicionado" in raw or "ar condicionado" in raw or "arcondicionados" in raw or "ar-condicionados" in raw:
        # Verifica sub-features (ventilador, aquecedor, temperatura, velocidade, tela)
        text_lower = text.lower()
        
        # FAN (ventilador)
        if any(feat in text_lower for feat in CLIMATE_FEATURES["fan"]):
            action_on = any(a in words for a in ACTIONS_ON)
            action_off = any(a in words for a in ACTIONS_OFF)
            
            if not action_on and not action_off:
                return {
                    "intent": "error",
                    "domain": "climate",
                    "response": "Você quer ligar ou desligar o ventilador?",
                    "text": text
                }
            
            action = "on" if action_on else "off"
            room = extract_room_from_climate(raw, text_lower)
            
            return {
                "intent": f"fan_{action}",
                "domain": "climate",
                "room": room,
                "text": text
            }
        
        # HEATER (aquecedor)
        if any(feat in text_lower for feat in CLIMATE_FEATURES["heater"]):
            action_on = any(a in words for a in ACTIONS_ON)
            action_off = any(a in words for a in ACTIONS_OFF)
            
            if not action_on and not action_off:
                return {
                    "intent": "error",
                    "domain": "climate",
                    "response": "Você quer ligar ou desligar o aquecedor?",
                    "text": text
                }
            
            action = "on" if action_on else "off"
            room = extract_room_from_climate(raw, text_lower)
            
            return {
                "intent": f"heater_{action}",
                "domain": "climate",
                "room": room,
                "text": text
            }
        
        # DISPLAY (tela)
        if any(feat in text_lower for feat in CLIMATE_FEATURES["display"]):
            if any(a in words for a in ACTIONS_OFF + ["desligar", "apagar"]):
                room = extract_room_from_climate(raw, text_lower)
                return {
                    "intent": "display_off",
                    "domain": "climate",
                    "room": room,
                    "text": text
                }
        
        # TEMPERATURE (temperatura)
        if any(feat in text_lower for feat in CLIMATE_FEATURES["temperature"]):
            temp_range = extract_temperature_range(text)
            if temp_range:
                room = extract_room_from_climate(raw, text_lower)
                return {
                    "intent": "set_temperature",
                    "domain": "climate",
                    "room": room,
                    "value": temp_range[0],  # Usa primeiro valor do range como temperatura
                    "text": text
                }
            
            temp = extract_number(text)
            if temp:
                room = extract_room_from_climate(raw, text_lower)
                return {
                    "intent": "set_temperature",
                    "domain": "climate",
                    "room": room,
                    "value": temp,
                    "text": text
                }
            
            return {
                "intent": "error",
                "domain": "climate",
                "response": "Qual temperatura você quer? Ex: 22 graus.",
                "text": text
            }
        
        # SPEED (velocidade do ventilador)
        if any(feat in text_lower for feat in CLIMATE_FEATURES["speed"]):
            if "aumentar" in text_lower or "aumentar" in raw or "subir" in raw:
                room = extract_room_from_climate(raw, text_lower)
                return {
                    "intent": "increase_speed",
                    "domain": "climate",
                    "room": room,
                    "text": text
                }
            
            if "abaixar" in text_lower or "diminuir" in text_lower or "reduzir" in raw:
                room = extract_room_from_climate(raw, text_lower)
                return {
                    "intent": "decrease_speed",
                    "domain": "climate",
                    "room": room,
                    "text": text
                }
            
            speed = extract_number(text)
            if speed:
                room = extract_room_from_climate(raw, text_lower)
                return {
                    "intent": "set_speed",
                    "domain": "climate",
                    "room": room,
                    "value": speed,
                    "text": text
                }
            
            return {
                "intent": "error",
                "domain": "climate",
                "response": "Qual velocidade? Ex: velocidade 2",
                "text": text
            }
        
        # ---- LIGAR/DESLIGAR AR (comportamento existente)
        # Detecta ação
        action_on = any(a in words for a in ACTIONS_ON)
        action_off = any(a in words for a in ACTIONS_OFF)
        
        if not action_on and not action_off:
            return {
                "intent": "error",
                "domain": "climate",
                "response": "Você quer ligar ou desligar o ar?",
                "text": text
            }
        
        action = "on" if action_on else "off"
        
        # Detecta plural no TEXTO ORIGINAL (antes de normalizar, para pegar "os")
        is_plural = any(term in text_lower for term in [
            "todos", 
            "os dois", 
            "dois ar", 
            "arcondicionados",
            "ar-condicionados",
            "todos ar",
            "todos ar-",
            "todos arcondicionado"
        ])
        
        # Se plural, retorna all_on/all_off
        if is_plural:
            return {
                "intent": "all_on" if action == "on" else "all_off",
                "domain": "climate",
                "text": text
            }
        
        # Singular: remove palavras de ação e tipo, mantendo somente o cômodo
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
