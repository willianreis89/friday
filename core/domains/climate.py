from core.context_manager import context
from core.ha_client import call_service, get_state
from utils.logger import log_action, setup_logger

logger = setup_logger(__name__)

# ---------------- DEVICES ----------------

CLIMATE_DEVICES = {
    "quarto": {
        "power_on": "script.gelar_ar_lg_quarto",
        "power_off": "script.desligar_ar_lg_quarto",
        "fan_on": "script.ventilar_ar_lg_quarto",
        "fan_off": "script.desligar_ar_lg_quarto",
        "heater_on": "script.quente_ar_lg_quarto",
        "heater_off": "script.desligar_ar_lg_quarto",
        "temperature": "input_number.temperature_quarto",
        "fan_speed": "input_number.fan_speed_quarto",
        "display_off": ("remote.broadlink_remote_bedroom", "DisplayOff"),
        "state": "binary_sensor.ar_condicionado_quarto_contact"
    },
    "closet": {
        "power_on": "script.gelar_ar_lg_closet",
        "power_off": "script.desligar_ar_lg_closet",
        "fan_on": "script.ventilar_ar_lg_closet",
        "fan_off": "script.desligar_ar_lg_closet",
        "heater_on": None,  # closet não tem aquecedor
        "heater_off": None,
        "temperature": "input_number.temperature_escritorio",
        "fan_speed": "input_number.fan_speed_escritorio",
        "display_off": None,  # closet não tem display
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
                logger.debug(f"Comodo identificado: '{search}' -> {room}")
                return room
    logger.debug(f"Nenhum comodo identificado para: '{search}'")
    return None

def is_generic_ar(search: str):
    return not search or search in GENERIC_AR

def is_on(entity_id: str):
    return get_state(entity_id) == "on"

# -------- SUB-FEATURE HANDLERS --------

def handle_fan_on(intent: dict):
    """Liga o ventilador do ar-condicionado."""
    room = intent.get("room")
    logger.info(f"Ligando ventilador do ar do {room}")
    
    if not room or room not in CLIMATE_DEVICES:
        return {"message": "Qual cômodo? Quarto ou closet?"}
    
    cfg = CLIMATE_DEVICES[room]
    script = cfg.get("fan_on")
    
    if not script:
        return {"message": f"Ventilador não disponível no {room}."}
    
    call_service("script", script.replace("script.", ""), {})
    log_action(logger, "climate", "fan_on", room)
    return {"message": f"Ventilador do {room} ligado."}

def handle_fan_off(intent: dict):
    """Desliga o ventilador do ar-condicionado."""
    room = intent.get("room")
    logger.info(f"Desligando ventilador do ar do {room}")
    
    if not room or room not in CLIMATE_DEVICES:
        return {"message": "Qual cômodo? Quarto ou closet?"}
    
    cfg = CLIMATE_DEVICES[room]
    script = cfg.get("fan_off")
    
    if not script:
        return {"message": f"Ventilador não disponível no {room}."}
    
    call_service("script", script.replace("script.", ""), {})
    log_action(logger, "climate", "fan_off", room)
    return {"message": f"Ventilador do {room} desligado."}

def handle_heater_on(intent: dict):
    """Liga o aquecedor do ar-condicionado."""
    room = intent.get("room")
    logger.info(f"Ligando aquecedor do ar do {room}")
    
    if not room or room not in CLIMATE_DEVICES:
        return {"message": "Qual cômodo? Quarto ou closet?"}
    
    cfg = CLIMATE_DEVICES[room]
    script = cfg.get("heater_on")
    
    if not script:
        return {"message": f"Aquecedor não disponível no {room}."}
    
    call_service("script", script.replace("script.", ""), {})
    log_action(logger, "climate", "heater_on", room)
    return {"message": f"Aquecedor do {room} ligado."}

def handle_heater_off(intent: dict):
    """Desliga o aquecedor do ar-condicionado."""
    room = intent.get("room")
    logger.info(f"Desligando aquecedor do ar do {room}")
    
    if not room or room not in CLIMATE_DEVICES:
        return {"message": "Qual cômodo? Quarto ou closet?"}
    
    cfg = CLIMATE_DEVICES[room]
    script = cfg.get("heater_off")
    
    if not script:
        return {"message": f"Aquecedor não disponível no {room}."}
    
    call_service("script", script.replace("script.", ""), {})
    log_action(logger, "climate", "heater_off", room)
    return {"message": f"Aquecedor do {room} desligado."}

def handle_display_off(intent: dict):
    """Apaga a tela do ar-condicionado via controle remoto."""
    room = intent.get("room")
    logger.info(f"Apagando tela do ar do {room}")
    
    if not room or room not in CLIMATE_DEVICES:
        return {"message": "Qual cômodo? Quarto ou closet?"}
    
    cfg = CLIMATE_DEVICES[room]
    remote_data = cfg.get("display_off")
    
    if not remote_data:
        return {"message": f"Controle remoto não disponível no {room}."}
    
    remote_entity, command = remote_data
    call_service("remote", "send_command", {
        "entity_id": remote_entity,
        "device": "SmartInverter",
        "command": command
    })
    log_action(logger, "climate", "display_off", room)
    return {"message": f"Tela do ar do {room} apagada."}

def handle_set_temperature(intent: dict):
    """Define a temperatura do ar-condicionado."""
    room = intent.get("room")
    temp = intent.get("value")
    logger.info(f"Definindo temperatura do ar do {room} para {temp}°C")
    
    if not room or room not in CLIMATE_DEVICES:
        return {"message": "Qual cômodo? Quarto ou closet?"}
    
    if temp is None:
        return {"message": "Qual temperatura? Ex: 22 graus."}
    
    # Valida range (18-26°C)
    if not (18 <= temp <= 26):
        return {"message": f"Temperatura deve estar entre 18 e 26°C. Você pediu {temp}°C."}
    
    cfg = CLIMATE_DEVICES[room]
    temp_entity = cfg.get("temperature")
    
    if not temp_entity:
        return {"message": f"Controle de temperatura não disponível no {room}."}
    
    call_service("input_number", "set_value", {
        "entity_id": temp_entity,
        "value": temp
    })
    log_action(logger, "climate", f"temperature_{temp}", room)
    return {"message": f"Temperatura do {room} definida para {temp}°C."}

def handle_set_speed(intent: dict):
    """Define a velocidade do ventilador (1-3)."""
    room = intent.get("room")
    speed = intent.get("value")
    logger.info(f"Definindo velocidade do ar do {room} para {speed}")
    
    if not room or room not in CLIMATE_DEVICES:
        return {"message": "Qual cômodo? Quarto ou closet?"}
    
    if speed is None:
        return {"message": "Qual velocidade? Ex: velocidade 2."}
    
    # Valida range (1-3)
    if not (1 <= speed <= 3):
        return {"message": f"Velocidade deve estar entre 1 e 3. Você pediu {speed}."}
    
    cfg = CLIMATE_DEVICES[room]
    speed_entity = cfg.get("fan_speed")
    
    if not speed_entity:
        return {"message": f"Controle de velocidade não disponível no {room}."}
    
    call_service("input_number", "set_value", {
        "entity_id": speed_entity,
        "value": speed
    })
    log_action(logger, "climate", f"speed_{speed}", room)
    return {"message": f"Velocidade do {room} definida para {speed}."}

def handle_increase_speed(intent: dict):
    """Aumenta a velocidade do ventilador."""
    room = intent.get("room")
    logger.info(f"Aumentando velocidade do ar do {room}")
    
    if not room or room not in CLIMATE_DEVICES:
        return {"message": "Qual cômodo? Quarto ou closet?"}
    
    cfg = CLIMATE_DEVICES[room]
    speed_entity = cfg.get("fan_speed")
    
    if not speed_entity:
        return {"message": f"Controle de velocidade não disponível no {room}."}
    
    # Pega valor atual e incrementa
    current = get_state(speed_entity)
    try:
        new_speed = min(int(float(current)) + 1, 3)  # Máximo 3
        call_service("input_number", "set_value", {
            "entity_id": speed_entity,
            "value": new_speed
        })
        log_action(logger, "climate", "increase_speed", room)
        return {"message": f"Velocidade do {room} aumentada para {new_speed}."}
    except (ValueError, TypeError):
        return {"message": "Não consegui aumentar a velocidade."}

def handle_decrease_speed(intent: dict):
    """Diminui a velocidade do ventilador."""
    room = intent.get("room")
    logger.info(f"Diminuindo velocidade do ar do {room}")
    
    if not room or room not in CLIMATE_DEVICES:
        return {"message": "Qual cômodo? Quarto ou closet?"}
    
    cfg = CLIMATE_DEVICES[room]
    speed_entity = cfg.get("fan_speed")
    
    if not speed_entity:
        return {"message": f"Controle de velocidade não disponível no {room}."}
    
    # Pega valor atual e decrementa
    current = get_state(speed_entity)
    try:
        new_speed = max(int(float(current)) - 1, 1)  # Mínimo 1
        call_service("input_number", "set_value", {
            "entity_id": speed_entity,
            "value": new_speed
        })
        log_action(logger, "climate", "decrease_speed", room)
        return {"message": f"Velocidade do {room} diminuída para {new_speed}."}
    except (ValueError, TypeError):
        return {"message": "Não consegui diminuir a velocidade."}



# -------- MAIN HANDLER --------

def handle(intent: dict):
    action = intent["intent"]
    logger.info(f"Processando climate.{action}")
    
    # Roteia para handlers de sub-features
    if action == "fan_on":
        return handle_fan_on(intent)
    if action == "fan_off":
        return handle_fan_off(intent)
    if action == "heater_on":
        return handle_heater_on(intent)
    if action == "heater_off":
        return handle_heater_off(intent)
    if action == "display_off":
        return handle_display_off(intent)
    if action == "set_temperature":
        return handle_set_temperature(intent)
    if action == "set_speed":
        return handle_set_speed(intent)
    if action == "increase_speed":
        return handle_increase_speed(intent)
    if action == "decrease_speed":
        return handle_decrease_speed(intent)
    
    # ---- LIGAR/DESLIGAR AR (comportamento existente)
    search = intent.get("search", "").lower()
    logger.info(f"Processando climate.{action} | Busca: '{search}'")

    # Ligar/desligar TODOS os ares
    if action in ("all_on", "all_off"):
        service_action = "on" if action == "all_on" else "off"
        for room, cfg in CLIMATE_DEVICES.items():
            script = cfg["power_on"] if service_action == "on" else cfg["power_off"]
            call_service("script", script.replace("script.", ""), {})
            log_action(logger, "climate", service_action, room)
        
        msg_action = "ligados" if service_action == "on" else "desligados"
        return {"message": f"Todos os ar-condicionados foram {msg_action}."}

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
            log_action(logger, "climate", "off", ligados[0]["room"])
            return {"message": f"Ar do {ligados[0]['room']} desligado."}

        logger.info(f"Multiplos ares ligados: {[l['room'] for l in ligados]}")
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
        log_action(logger, "climate", action, room)
        return {"message": f"Ar do {room} {'ligado' if action == 'on' else 'desligado'}."}

    logger.warning(f"Comando de ar-condicionado nao compreendido: '{search}'")
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
