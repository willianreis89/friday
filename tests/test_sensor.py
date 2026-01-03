"""
Testes para core.domains.sensor

Testa handlers de queries e comparações de sensores
"""
from unittest.mock import patch

import pytest

from core.domains.sensor import handle, get_sensor_value, format_sensor_value


class TestGetSensorValue:
    """Testes para obtenção de valores de sensores"""
    
    @patch('core.domains.sensor.get_state')
    def test_get_temperature_quarto(self, mock_get_state):
        """Deve obter temperatura do quarto"""
        mock_get_state.return_value = "23.5"
        
        value, entity_id = get_sensor_value("temperature", "quarto")
        
        assert value == "23.5"
        assert entity_id == "sensor.sensor_temp_quarto_temperature"
        mock_get_state.assert_called_once_with("sensor.sensor_temp_quarto_temperature")
    
    @patch('core.domains.sensor.get_state')
    def test_get_humidity_closet(self, mock_get_state):
        """Deve obter umidade do closet"""
        mock_get_state.return_value = "55"
        
        value, entity_id = get_sensor_value("humidity", "closet")
        
        assert value == "55"
        assert entity_id == "sensor.esp32relaysmesas_closet_room_humidity"
    
    def test_get_sensor_value_unknown_room(self):
        """Deve retornar None para cômodo desconhecido"""
        value, entity_id = get_sensor_value("temperature", "garagem")
        
        assert value is None
        assert entity_id == ""


class TestFormatSensorValue:
    """Testes para formatação de valores de sensores"""
    
    def test_format_temperature(self):
        """Deve formatar temperatura com unidade"""
        assert format_sensor_value("23.5", "temperature") == "23 graus"
        assert format_sensor_value("18", "temperature") == "18 graus"
    
    def test_format_humidity(self):
        """Deve formatar umidade com percentual"""
        assert format_sensor_value("55", "humidity") == "55 %"
    
    def test_format_none_value(self):
        """Deve retornar valor sem unidade para tipos desconhecidos"""
        assert format_sensor_value(None, "temperature") == "não disponível"


class TestQuerySensor:
    """Testes para query simples de sensor"""
    
    @patch('core.domains.sensor.get_state')
    def test_query_temperature_quarto(self, mock_get_state):
        """Deve retornar temperatura e umidade do quarto"""
        def mock_get_state_impl(entity_id):
            if "temperature" in entity_id:
                return "23"
            elif "humidity" in entity_id:
                return "55"
            return None
        
        mock_get_state.side_effect = mock_get_state_impl
        
        intent = {"intent": "query_sensor", "room": "quarto"}
        result = handle(intent)
        
        assert "temperatura" in result["message"].lower()
        assert "humidade" in result["message"].lower()
        assert "quarto" in result["message"].lower()
        assert "23" in result["message"]
        assert "55" in result["message"]
    
    @patch('core.domains.sensor.get_state')
    def test_query_temperature_closet(self, mock_get_state):
        """Deve retornar temperatura e umidade do closet"""
        def mock_get_state_impl(entity_id):
            if "temperature" in entity_id:
                return "20"
            elif "humidity" in entity_id:
                return "60"
            return None
        
        mock_get_state.side_effect = mock_get_state_impl
        
        intent = {"intent": "query_sensor", "room": "closet"}
        result = handle(intent)
        
        assert "20" in result["message"]
        assert "60" in result["message"]
        assert "closet" in result["message"].lower()
    
    @patch('core.domains.sensor.get_state')
    def test_query_temperature_externa(self, mock_get_state):
        """Deve retornar temperatura da externa/sacada"""
        def mock_get_state_impl(entity_id):
            if "temperature" in entity_id:
                return "25"
            elif "humidity" in entity_id:
                return "65"
            return None
        
        mock_get_state.side_effect = mock_get_state_impl
        
        intent = {"intent": "query_sensor", "room": "externa"}
        result = handle(intent)
        
        assert "externa/sacada" in result["message"].lower()
        assert "25" in result["message"]
        assert "65" in result["message"]
    
    def test_query_sensor_sem_comodo(self):
        """Deve retornar erro se cômodo não especificado"""
        intent = {"intent": "query_sensor", "room": None}
        result = handle(intent)
        
        assert "comodo" in result["message"].lower() or "qual" in result["message"].lower()
    
    @patch('core.domains.sensor.get_state')
    def test_query_sensor_value_unavailable(self, mock_get_state):
        """Deve retornar erro se valor não disponível"""
        mock_get_state.return_value = None
        
        intent = {"intent": "query_sensor", "room": "quarto"}
        result = handle(intent)
        
        assert "consegui" in result["message"].lower() or "não disponível" in result["message"].lower()


class TestCompareSensors:
    """Testes para comparação de dois sensores"""
    
    @patch('core.domains.sensor.get_sensor_value')
    def test_compare_two_rooms_temperature(self, mock_get_sensor):
        """Deve comparar temperatura entre dois cômodos"""
        # Mock retorna valores diferentes para diferentes rooms
        def get_sensor_side_effect(sensor_type, room):
            if room == "quarto":
                return ("25", "sensor.temperatura_quarto")
            elif room == "closet":
                return ("23", "sensor.temperatura_escritorio")
            return (None, "")
        
        mock_get_sensor.side_effect = get_sensor_side_effect
        
        intent = {
            "intent": "compare_sensors",
            "sensor_type": "temperature",
            "rooms": ["quarto", "closet"]
        }
        result = handle(intent)
        
        assert "quarto" in result["message"].lower()
        assert "25" in result["message"]
        assert "23" in result["message"]
        assert "quente" in result["message"].lower()
    
    @patch('core.domains.sensor.get_sensor_value')
    def test_compare_closet_warmer_than_quarto(self, mock_get_sensor):
        """Deve identificar qual ambiente está mais quente"""
        def get_sensor_side_effect(sensor_type, room):
            if room == "closet":
                return ("26", "sensor.temperatura_escritorio")
            elif room == "quarto":
                return ("22", "sensor.temperatura_quarto")
            return (None, "")
        
        mock_get_sensor.side_effect = get_sensor_side_effect
        
        intent = {
            "intent": "compare_sensors",
            "sensor_type": "temperature",
            "rooms": ["quarto", "closet"]
        }
        result = handle(intent)
        
        assert "closet" in result["message"].lower()
        assert "26" in result["message"]
        assert "quente" in result["message"].lower()
    
    @patch('core.domains.sensor.get_sensor_value')
    def test_compare_humidity_two_rooms(self, mock_get_sensor):
        """Deve comparar umidade entre dois cômodos"""
        def get_sensor_side_effect(sensor_type, room):
            if room == "quarto":
                return ("60", "sensor.umidade_quarto")
            elif room == "closet":
                return ("50", "sensor.umidade_escritorio")
            return (None, "")
        
        mock_get_sensor.side_effect = get_sensor_side_effect
        
        intent = {
            "intent": "compare_sensors",
            "sensor_type": "humidity",
            "rooms": ["quarto", "closet"]
        }
        result = handle(intent)
        
        assert "umidade" in result["message"].lower()
        assert "60" in result["message"]
    
    def test_compare_sem_rooms(self):
        """Deve retornar erro se sem cômodos para comparar"""
        intent = {"intent": "compare_sensors", "sensor_type": "temperature", "rooms": []}
        result = handle(intent)
        
        assert "dois" in result["message"].lower() or "ambientes" in result["message"].lower()
    
    def test_compare_com_um_room(self):
        """Deve retornar erro se apenas um cômodo"""
        intent = {"intent": "compare_sensors", "sensor_type": "temperature", "rooms": ["quarto"]}
        result = handle(intent)
        
        assert "dois" in result["message"].lower() or "ambientes" in result["message"].lower()


class TestCompareAllSensors:
    """Testes para comparação de todos os sensores"""
    
    @patch('core.domains.sensor.get_sensor_value')
    def test_compare_all_find_warmest(self, mock_get_sensor):
        """Deve encontrar o ambiente mais quente"""
        def get_sensor_side_effect(sensor_type, room):
            temps = {
                "quarto": ("25", "sensor.temperatura_quarto"),
                "closet": ("23", "sensor.temperatura_escritorio"),
                "sala": ("22", "sensor.temperatura_sala")
            }
            return temps.get(room, (None, ""))
        
        mock_get_sensor.side_effect = get_sensor_side_effect
        
        intent = {
            "intent": "compare_all_sensors",
            "sensor_type": "temperature",
            "comparison_type": "highest"
        }
        result = handle(intent)
        
        assert "quarto" in result["message"].lower()
        assert "quente" in result["message"].lower()
        assert "25" in result["message"]
    
    @patch('core.domains.sensor.get_sensor_value')
    def test_compare_all_find_coldest(self, mock_get_sensor):
        """Deve encontrar o ambiente mais frio"""
        def get_sensor_side_effect(sensor_type, room):
            temps = {
                "quarto": ("25", "sensor.temperatura_quarto"),
                "closet": ("20", "sensor.temperatura_escritorio"),
                "sala": ("22", "sensor.temperatura_sala")
            }
            return temps.get(room, (None, ""))
        
        mock_get_sensor.side_effect = get_sensor_side_effect
        
        intent = {
            "intent": "compare_all_sensors",
            "sensor_type": "temperature",
            "comparison_type": "lowest"
        }
        result = handle(intent)
        
        assert "frio" in result["message"].lower()
        assert "20" in result["message"]
    
    @patch('core.domains.sensor.get_sensor_value')
    def test_compare_all_humidity_highest(self, mock_get_sensor):
        """Deve encontrar o ambiente com maior umidade"""
        def get_sensor_side_effect(sensor_type, room):
            humidities = {
                "quarto": ("70", "sensor.umidade_quarto"),
                "closet": ("55", "sensor.umidade_escritorio"),
                "sala": ("60", "sensor.umidade_sala")
            }
            return humidities.get(room, (None, ""))
        
        mock_get_sensor.side_effect = get_sensor_side_effect
        
        intent = {
            "intent": "compare_all_sensors",
            "sensor_type": "humidity",
            "comparison_type": "highest"
        }
        result = handle(intent)
        
        assert "maior umidade" in result["message"].lower()
        assert "70" in result["message"]
    
    @patch('core.domains.sensor.get_state')
    def test_compare_all_no_data(self, mock_get_state):
        """Deve retornar erro se nenhum dado disponível"""
        mock_get_state.return_value = None
        
        intent = {
            "intent": "compare_all_sensors",
            "sensor_type": "temperature",
            "comparison_type": "highest"
        }
        result = handle(intent)
        
        assert "consegui" in result["message"].lower() or "não disponível" in result["message"].lower()


class TestSensorIntegration:
    """Testes de integração do módulo sensor"""
    
    @patch('core.domains.sensor.get_state')
    def test_handle_query_routes_correctly(self, mock_get_state):
        """Deve rotear query_sensor para handler correto"""
        mock_get_state.return_value = "23"
        
        intent = {"intent": "query_sensor", "sensor_type": "temperature", "room": "quarto"}
        result = handle(intent)
        
        assert "message" in result
        assert isinstance(result["message"], str)
    
    @patch('core.domains.sensor.get_sensor_value')
    def test_handle_compare_routes_correctly(self, mock_get_sensor):
        """Deve rotear compare_sensors para handler correto"""
        def get_sensor_side_effect(sensor_type, room):
            if room == "quarto":
                return ("25", "sensor.temperatura_quarto")
            return ("20", "sensor.temperatura_closet")
        
        mock_get_sensor.side_effect = get_sensor_side_effect
        
        intent = {
            "intent": "compare_sensors",
            "sensor_type": "temperature",
            "rooms": ["quarto", "closet"]
        }
        result = handle(intent)
        
        assert "message" in result
        assert isinstance(result["message"], str)
    
    def test_handle_unknown_intent(self):
        """Deve retornar erro para intent desconhecido"""
        intent = {"intent": "unknown_sensor_intent", "domain": "sensor"}
        result = handle(intent)
        
        assert "message" in result
        assert "entendi" in result["message"].lower() or "query" in result["message"].lower()
