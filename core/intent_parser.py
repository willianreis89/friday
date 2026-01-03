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

def extract_room_for_query(text_lower: str) -> str | None:
    """Extrai cômodo de uma query de sensor."""
    if "quarto" in text_lower:
        return "quarto"
    if "closet" in text_lower:
        return "closet"
    if "banheiro" in text_lower:
        return "banheiro"
    if "externa" in text_lower or "sacada" in text_lower:
        return "externa"
    return None

def extract_rooms_for_comparison(text_lower: str) -> list[str]:
    """Extrai múltiplos cômodos de uma comparação."""
    rooms = []
    room_keywords = {
        "quarto": ["quarto"],
        "closet": ["closet"],
        "banheiro": ["banheiro"],
        "externa": ["externa", "sacada"]
    }
    
    for room_name, keywords in room_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                rooms.append(room_name)
                break
    
    return rooms

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

# Sensor query patterns
SENSOR_QUERY_PATTERNS = {
    "temperature": ["temperatura", "graus", "quente", "frio", "como está"],
    "humidity": ["umidade", "úmidade"],
    "light": ["luminosidade", "claridade"],
    "motion": ["movimento", "detectou"],
    "window": ["janela", "janelas", "aberta", "aberto", "fechada", "fechado"]
}

# Sensor comparison patterns (para comparações entre ambientes)
SENSOR_COMPARISONS = {
    "which_highest": ["qual", "mais quente", "mais frio", "mais alta", "mais baixa"],
    "which_lowest": ["onde está mais frio", "qual está mais frio"],
    "compare_two": ["ou", "comparação"]
}

# ------------------ PARSER ------------------

def parse(text: str):
    raw = normalize(text)
    text_lower = text.lower()

    # ---- SENSOR QUERIES (HIGH PRIORITY - check before climate)
    # Check if this is a query/question with sensor keywords
    # Pergunta típica: "Qual a temperatura do quarto?" "Onde está mais quente?" "A janela está aberta?"
    # Use word boundaries to avoid matching "temperatura" when looking for "tem"
    query_words = ["qual ", "quais ", "quanto ", "como está", "quantos ", "onde ", " tem "]
    is_asking = any(keyword in (" " + text_lower + " ") for keyword in query_words)
    
    # Special handling for "está" and "esta" - only treat as question if it's about windows
    if not is_asking and ("está" in text_lower or "esta" in text_lower):
        # Check if it's a window query like "A janela está aberta?"
        if "janela" in text_lower:
            is_asking = True
    
    # If it's a question (qual, quanto, etc) and has no climate action keywords (ligar, desligar, aumentar, diminuir, setar, colocar)
    # then treat as sensor query
    if is_asking:
        has_climate_action = any(
            action in text_lower 
            for action in ACTIONS_ON + ACTIONS_OFF + ["aumentar", "diminuir", "subir", "reduzir", "setar", "colocar", "definir"]
        )
        
        # If no climate action intent, check for sensor keywords
        if not has_climate_action:
            is_sensor_query = any(
                pattern in text_lower 
                for pattern_type in SENSOR_QUERY_PATTERNS.values()
                for pattern in pattern_type
            )
            
            if is_sensor_query:
                # Detecta tipo de sensor
                sensor_type = None
                if any(t in text_lower for t in SENSOR_QUERY_PATTERNS["temperature"]):
                    sensor_type = "temperature"
                elif any(t in text_lower for t in SENSOR_QUERY_PATTERNS["humidity"]):
                    sensor_type = "humidity"
                elif any(t in text_lower for t in SENSOR_QUERY_PATTERNS["light"]):
                    sensor_type = "light"
                elif any(t in text_lower for t in SENSOR_QUERY_PATTERNS["motion"]):
                    sensor_type = "motion"
                elif any(t in text_lower for t in SENSOR_QUERY_PATTERNS["window"]):
                    sensor_type = "window"
                
                if sensor_type:
                    # Special handling for window queries
                    if sensor_type == "window":
                        # "Quais janelas estão abertas?" or "Tem alguma janela aberta?"
                        if "quais" in text_lower or "tem" in text_lower or "alguma" in text_lower:
                            # Check if asking about all windows or specific state
                            if "aberta" in text_lower or "aberto" in text_lower:
                                return {
                                    "intent": "list_windows_open",
                                    "domain": "sensor",
                                    "sensor_type": "window",
                                    "state": "open",
                                    "text": text
                                }
                            elif "fechada" in text_lower or "fechado" in text_lower:
                                return {
                                    "intent": "list_windows_closed",
                                    "domain": "sensor",
                                    "sensor_type": "window",
                                    "state": "closed",
                                    "text": text
                                }
                        
                        # Check for general window query without room: "A janela está aberta?"
                        room = extract_room_for_query(text_lower)
                        if room:
                            # Specific window query: "A janela do closet esta aberta?"
                            is_open_question = "aberta" in text_lower or "aberto" in text_lower
                            is_closed_question = "fechada" in text_lower or "fechado" in text_lower
                            
                            if is_open_question or is_closed_question:
                                return {
                                    "intent": "query_window",
                                    "domain": "sensor",
                                    "sensor_type": "window",
                                    "room": room,
                                    "question_type": "open" if is_open_question else "closed",
                                    "text": text
                                }
                        else:
                            # General window query without specific room
                            if "aberta" in text_lower or "aberto" in text_lower:
                                return {
                                    "intent": "list_windows_open",
                                    "domain": "sensor",
                                    "sensor_type": "window",
                                    "state": "open",
                                    "text": text
                                }
                            elif "fechada" in text_lower or "fechado" in text_lower:
                                return {
                                    "intent": "list_windows_closed",
                                    "domain": "sensor",
                                    "sensor_type": "window",
                                    "state": "closed",
                                    "text": text
                                }
                    
                    # Detecta comparação (múltiplos ambientes) - não para windows
                    if sensor_type != "window":
                        has_comparison = " ou " in text_lower or "vs" in text_lower or "mais" in text_lower
                        
                        if has_comparison:
                            # Extrai dois ambientes para comparar
                            rooms = extract_rooms_for_comparison(text_lower)
                            if len(rooms) >= 2:
                                return {
                                    "intent": "compare_sensors",
                                    "domain": "sensor",
                                    "sensor_type": sensor_type,
                                    "rooms": rooms,
                                    "text": text
                                }
                            elif "mais" in text_lower and ("quente" in text_lower or "frio" in text_lower or "alta" in text_lower or "baixa" in text_lower):
                                # Query como "qual ambiente está mais quente" - precisa comparar todos
                                return {
                                    "intent": "compare_all_sensors",
                                    "domain": "sensor",
                                    "sensor_type": sensor_type,
                                    "comparison_type": "highest" if ("quente" in text_lower or "alta" in text_lower) else "lowest",
                                    "text": text
                                }
                        
                        # Query simples de um sensor
                        room = extract_room_for_query(text_lower)
                        
                        return {
                            "intent": "query_sensor",
                            "domain": "sensor",
                            "sensor_type": sensor_type,
                            "room": room,
                            "text": text
                        }


    # ---- VERIFICA FEATURES DE CLIMATE (antes de checar por "ar")
    
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
    # ============================================================
    # LIGHT PARSING
    # ============================================================
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

    # Detecta ação (ligar/desligar)
    words = raw.split()
    action_on = any(a in words for a in ACTIONS_ON)
    action_off = any(a in words for a in ACTIONS_OFF)
    
    # Detecta múltiplos comandos com "e"
    if " e " in raw and (action_on or action_off):
        return {
            "intent": "multi",
            "domain": "light",
            "text": text
        }
    
    if not action_on and not action_off:
        return {
            "intent": "error",
            "domain": "light",
            "response": "Você quer ligar ou desligar a luz?",
            "text": text
        }
    
    action = "on" if action_on else "off"
    
    # Detecta se é plural (todas as luzes)
    is_plural = any(term in text_lower for term in ["todas", "os", "as"])
    
    if is_plural:
        return {
            "intent": "all_" + action,
            "domain": "light",
            "type": light_type,
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
