from core.ha_client import get_state
from utils.logger import setup_logger

logger = setup_logger(__name__)

# ============================================================
# ======================== DEVICES =========================
# ============================================================

# Mapping de cômodos para sensores de temperatura
SENSOR_MAPPING = {
    "temperature": {
        "externa": "sensor.sensor_temp_outside_temperature",
        "sacada": "sensor.sensor_temp_outside_temperature",
        "closet": "sensor.esp32relaysmesas_closet_room_temperature",
        "quarto": "sensor.sensor_temp_quarto_temperature",
    },
    "humidity": {
        "externa": "sensor.sensor_temp_outside_humidity",
        "sacada": "sensor.sensor_temp_outside_humidity",
        "closet": "sensor.esp32relaysmesas_closet_room_humidity",
        "quarto": "sensor.sensor_temp_quarto_humidity",
    },
    "window": {
        "closet": "binary_sensor.janela_closet_contact",
        "quarto": "binary_sensor.janela_quarto_contact",
        "banheiro": "binary_sensor.sonoff_1001879d3a",
    }
}

# Nomes de exibição dos cômodos
ROOM_DISPLAY_NAMES = {
    "externa": "externa/sacada",
    "sacada": "externa/sacada",
    "closet": "closet",
    "quarto": "quarto",
    "banheiro": "banheiro"
}

# Unidades e formatação
SENSOR_UNITS = {
    "temperature": "graus",
    "humidity": "%"
}

# ============================================================
# ======================== UTILS ============================
# ============================================================

def get_sensor_value(sensor_type: str, room: str) -> tuple[str | None, str]:
    """
    Obtém o valor de um sensor específico.
    
    Returns:
        (value, entity_id) ou (None, entity_id) se não encontrado
    """
    entity_id = SENSOR_MAPPING.get(sensor_type, {}).get(room)
    
    if not entity_id:
        return None, ""
    
    try:
        value = get_state(entity_id)
        return value, entity_id
    except Exception as e:
        logger.warning(f"Erro ao obter valor de {entity_id}: {e}")
        return None, entity_id

def format_sensor_value(value: str, sensor_type: str) -> str:
    """Formata o valor do sensor com unidade apropriada."""
    if value is None:
        return "não disponível"
    
    unit = SENSOR_UNITS.get(sensor_type, "")
    
    if sensor_type == "temperature":
        # Remove decimais se houver, mantém inteiro
        try:
            temp = float(value)
            return f"{int(temp)} {unit}"
        except (ValueError, TypeError):
            return value
    
    if sensor_type == "motion":
        return "detectado" if value == "on" else "não detectado"
    
    if unit:
        return f"{value} {unit}"
    return value

def get_room_display_name(room: str) -> str:
    """Retorna o nome do cômodo em formato amigável."""
    return ROOM_DISPLAY_NAMES.get(room, room)

# ============================================================
# ===================== MAIN HANDLER ========================
# ============================================================

def handle(intent: dict):
    """Roteia para os handlers apropriados."""
    action = intent.get("intent")
    logger.info(f"Processando sensor.{action}")
    
    if action == "query_sensor":
        return handle_query_sensor(intent)
    elif action == "compare_sensors":
        return handle_compare_sensors(intent)
    elif action == "compare_all_sensors":
        return handle_compare_all_sensors(intent)
    elif action == "query_window":
        return handle_query_window(intent)
    elif action == "list_windows_open":
        return handle_list_windows_open(intent)
    elif action == "list_windows_closed":
        return handle_list_windows_closed(intent)
    
    return {"message": "Não entendi a query de sensor."}

# ============================================================
# =================== QUERY HANDLERS ========================
# ============================================================

def handle_query_sensor(intent: dict):
    """
    Obtém temperatura e umidade de um cômodo.
    
    Exemplo: "Qual a temperatura do quarto?"
    Response: "A temperatura do quarto é de 23 graus e a humidade é de 45%."
    """
    room = intent.get("room")
    
    logger.info(f"Query sensor do {room}")
    
    if not room:
        return {"message": "Qual cômodo você quer verificar?"}
    
    try:
        temp_value, temp_entity = get_sensor_value("temperature", room)
        humidity_value, humidity_entity = get_sensor_value("humidity", room)
        
        if temp_value is None or humidity_value is None:
            room_name = get_room_display_name(room)
            return {"message": f"Não consegui obter dados para {room_name}."}
        
        temp_formatted = format_sensor_value(temp_value, "temperature")
        humidity_formatted = format_sensor_value(humidity_value, "humidity")
        room_name = get_room_display_name(room)
        
        return {"message": f"A temperatura do {room_name} é de {temp_formatted} e a humidade é de {humidity_formatted}."}
    except Exception as e:
        logger.error(f"Erro ao buscar sensores: {str(e)}")
        return {"message": f"Erro ao buscar dados dos sensores."}

def handle_compare_sensors(intent: dict):
    """
    Compara sensores de dois ambientes.
    
    Exemplo: "Qual ambiente está mais quente, quarto ou closet?"
    Response: "O quarto está mais quente, com 25 graus. O closet está com 23 graus."
    """
    sensor_type = intent.get("sensor_type")
    rooms = intent.get("rooms", [])
    
    if len(rooms) < 2:
        return {"message": "Preciso de pelo menos dois ambientes para comparar."}
    
    logger.info(f"Comparando {sensor_type} entre {rooms}")
    
    # Obtém valores dos dois ambientes
    values = {}
    for room in rooms:
        value, _ = get_sensor_value(sensor_type, room)
        if value is not None:
            try:
                # Tenta converter para float para comparação numérica
                values[room] = float(value)
            except (ValueError, TypeError):
                values[room] = value
    
    if len(values) < 2:
        return {"message": "Não consegui obter dados suficientes dos ambientes."}
    
    # Determina qual é maior/menor
    if sensor_type in ["temperature", "humidity", "light"]:
        # Para estes, maior é melhor para comparação
        sorted_rooms = sorted(values.items(), key=lambda x: x[1], reverse=True)
        
        room1, value1 = sorted_rooms[0]
        room2, value2 = sorted_rooms[1]
        
        room1_display = get_room_display_name(room1)
        room2_display = get_room_display_name(room2)
        
        formatted_val1 = format_sensor_value(str(value1), sensor_type)
        formatted_val2 = format_sensor_value(str(value2), sensor_type)
        
        # Mensagem de comparação
        if sensor_type == "temperature":
            if value1 > value2:
                return {
                    "message": f"O {room1_display} está mais quente, com {formatted_val1}. "
                              f"O {room2_display} está com {formatted_val2}."
                }
            else:
                return {
                    "message": f"O {room2_display} está mais quente, com {formatted_val2}. "
                              f"O {room1_display} está com {formatted_val1}."
                }
        elif sensor_type == "humidity":
            if value1 > value2:
                return {
                    "message": f"O {room1_display} tem mais umidade, com {formatted_val1}. "
                              f"O {room2_display} tem {formatted_val2}."
                }
            else:
                return {
                    "message": f"O {room2_display} tem mais umidade, com {formatted_val2}. "
                              f"O {room1_display} tem {formatted_val1}."
                }
    
    return {"message": "Não consegui comparar os valores dos ambientes."}

def handle_compare_all_sensors(intent: dict):
    """
    Compara sensores de todos os ambientes e retorna o maior/menor.
    
    Exemplo: "Qual ambiente está mais quente?"
    Response: "O quarto está mais quente, com 25 graus."
    """
    sensor_type = intent.get("sensor_type")
    comparison_type = intent.get("comparison_type", "highest")
    
    logger.info(f"Comparando {sensor_type} entre todos os ambientes ({comparison_type})")
    
    # Obtém valores de todos os cômodos
    all_values = {}
    for room in SENSOR_MAPPING[sensor_type].keys():
        value, _ = get_sensor_value(sensor_type, room)
        if value is not None:
            try:
                all_values[room] = float(value)
            except (ValueError, TypeError):
                all_values[room] = value
    
    if not all_values:
        return {"message": f"Não consegui obter dados de {sensor_type}."}
    
    if comparison_type == "highest":
        best_room = max(all_values.items(), key=lambda x: x[1])
    else:  # lowest
        best_room = min(all_values.items(), key=lambda x: x[1])
    
    room, value = best_room
    room_display = get_room_display_name(room)
    formatted_value = format_sensor_value(str(value), sensor_type)
    
    if sensor_type == "temperature":
        if comparison_type == "highest":
            return {
                "message": f"O {room_display} está mais quente, com {formatted_value}."
            }
        else:
            return {
                "message": f"O {room_display} está mais frio, com {formatted_value}."
            }
    elif sensor_type == "humidity":
        if comparison_type == "highest":
            return {
                "message": f"O {room_display} tem a maior umidade, com {formatted_value}."
            }
        else:
            return {
                "message": f"O {room_display} tem a menor umidade, com {formatted_value}."
            }
    elif sensor_type == "light":
        if comparison_type == "highest":
            return {
                "message": f"O {room_display} tem a maior luminosidade, com {formatted_value}."
            }
        else:
            return {
                "message": f"O {room_display} tem a menor luminosidade, com {formatted_value}."
            }
    
    return {"message": f"O {room_display} tem o {sensor_type} em {formatted_value}."}
# ============================================================
# ==================== WINDOW HANDLERS ======================
# ============================================================

def handle_query_window(intent: dict):
    """
    Responde query específica de janela.
    
    Exemplo: "A janela do closet esta aberta?"
    Response: "Sim, está aberta." ou "Não, está fechada."
    """
    room = intent.get("room")
    question_type = intent.get("question_type")  # "open" or "closed"
    
    if not room:
        return {"message": "Qual janela você quer verificar?"}
    
    try:
        value, entity_id = get_sensor_value("window", room)
        
        if value is None:
            room_display = get_room_display_name(room)
            return {"message": f"Não consegui obter dados da janela do {room_display}."}
        
        room_display = get_room_display_name(room)
        is_open = value.lower() == "on"
        
        if question_type == "open":
            # User asked: "está aberta?"
            if is_open:
                return {"message": f"Sim, está aberta."}
            else:
                return {"message": f"Não, está fechada."}
        else:  # question_type == "closed"
            # User asked: "está fechada?"
            if is_open:
                return {"message": f"Não, está aberta."}
            else:
                return {"message": f"Sim, está fechada."}
    
    except Exception as e:
        logger.error(f"Erro ao buscar dados da janela: {str(e)}")
        return {"message": f"Erro ao buscar dados da janela."}

def handle_list_windows_open(intent: dict):
    """
    Lista as janelas abertas.
    
    Exemplo: "Quais janelas estão abertas?"
    Response: "A janela do quarto e do closet estão abertas."
    """
    try:
        open_windows = []
        
        for room in SENSOR_MAPPING["window"].keys():
            value, entity_id = get_sensor_value("window", room)
            if value and value.lower() == "on":
                open_windows.append(room)
        
        if not open_windows:
            return {"message": "Todas as janelas estão fechadas."}
        
        # Format response
        room_names = [get_room_display_name(room) for room in open_windows]
        
        if len(room_names) == 1:
            return {"message": f"A janela do {room_names[0]} está aberta."}
        else:
            # "A janela do quarto e do closet estão abertas"
            last = room_names.pop()
            rooms_str = " e do ".join(room_names) if room_names else ""
            if rooms_str:
                return {"message": f"A janela do {rooms_str} e do {last} estão abertas."}
            else:
                return {"message": f"A janela do {last} está aberta."}
    
    except Exception as e:
        logger.error(f"Erro ao listar janelas abertas: {str(e)}")
        return {"message": "Erro ao buscar status das janelas."}

def handle_list_windows_closed(intent: dict):
    """
    Lista as janelas fechadas.
    
    Exemplo: "Quais janelas estão fechadas?"
    Response: "A janela do banheiro está fechada."
    """
    try:
        closed_windows = []
        
        for room in SENSOR_MAPPING["window"].keys():
            value, entity_id = get_sensor_value("window", room)
            if value and value.lower() == "off":
                closed_windows.append(room)
        
        if not closed_windows:
            return {"message": "Todas as janelas estão abertas."}
        
        # Format response
        room_names = [get_room_display_name(room) for room in closed_windows]
        
        if len(room_names) == 1:
            return {"message": f"A janela do {room_names[0]} está fechada."}
        else:
            # "A janela do quarto e do closet estão fechadas"
            last = room_names.pop()
            rooms_str = " e do ".join(room_names) if room_names else ""
            if rooms_str:
                return {"message": f"A janela do {rooms_str} e do {last} estão fechadas."}
            else:
                return {"message": f"A janela do {last} está fechada."}
    
    except Exception as e:
        logger.error(f"Erro ao listar janelas fechadas: {str(e)}")
        return {"message": "Erro ao buscar status das janelas."}