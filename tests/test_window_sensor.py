"""
Testes para sensores de janelas

Testa queries de janelas abertas/fechadas
"""
from unittest.mock import patch
import pytest

from core.domains.sensor import handle


class TestQueryWindow:
    """Testes para queries de janelas específicas"""
    
    @patch('core.domains.sensor.get_state')
    def test_query_window_closet_open(self, mock_get_state):
        """Deve responder se janela do closet está aberta"""
        mock_get_state.return_value = "on"
        
        intent = {
            "intent": "query_window",
            "room": "closet",
            "question_type": "open"
        }
        result = handle(intent)
        
        assert "aberta" in result["message"].lower()
        assert "sim" in result["message"].lower()
    
    @patch('core.domains.sensor.get_state')
    def test_query_window_closet_closed(self, mock_get_state):
        """Deve responder se janela do closet está fechada"""
        mock_get_state.return_value = "off"
        
        intent = {
            "intent": "query_window",
            "room": "closet",
            "question_type": "closed"
        }
        result = handle(intent)
        
        assert "fechada" in result["message"].lower()
        assert "sim" in result["message"].lower()
    
    @patch('core.domains.sensor.get_state')
    def test_query_window_quarto_open_when_closed(self, mock_get_state):
        """Deve responder 'não' se janela do quarto não está aberta"""
        mock_get_state.return_value = "off"
        
        intent = {
            "intent": "query_window",
            "room": "quarto",
            "question_type": "open"
        }
        result = handle(intent)
        
        assert "fechada" in result["message"].lower()
        assert "não" in result["message"].lower()
    
    @patch('core.domains.sensor.get_state')
    def test_query_window_banheiro_closed_when_open(self, mock_get_state):
        """Deve responder 'não' se janela do banheiro não está fechada"""
        mock_get_state.return_value = "on"
        
        intent = {
            "intent": "query_window",
            "room": "banheiro",
            "question_type": "closed"
        }
        result = handle(intent)
        
        assert "aberta" in result["message"].lower()
        assert "não" in result["message"].lower()


class TestListWindowsOpen:
    """Testes para listar janelas abertas"""
    
    @patch('core.domains.sensor.get_state')
    def test_list_no_windows_open(self, mock_get_state):
        """Deve indicar se nenhuma janela está aberta"""
        mock_get_state.return_value = "off"
        
        intent = {"intent": "list_windows_open"}
        result = handle(intent)
        
        assert "fechadas" in result["message"].lower()
    
    @patch('core.domains.sensor.get_state')
    def test_list_one_window_open(self, mock_get_state):
        """Deve listar uma janela aberta"""
        def get_state_side_effect(entity_id):
            if "closet" in entity_id:
                return "on"
            return "off"
        
        mock_get_state.side_effect = get_state_side_effect
        
        intent = {"intent": "list_windows_open"}
        result = handle(intent)
        
        assert "closet" in result["message"].lower()
        assert "aberta" in result["message"].lower()
    
    @patch('core.domains.sensor.get_state')
    def test_list_multiple_windows_open(self, mock_get_state):
        """Deve listar múltiplas janelas abertas"""
        def get_state_side_effect(entity_id):
            if "closet" in entity_id or "quarto" in entity_id:
                return "on"
            return "off"
        
        mock_get_state.side_effect = get_state_side_effect
        
        intent = {"intent": "list_windows_open"}
        result = handle(intent)
        
        assert "closet" in result["message"].lower()
        assert "quarto" in result["message"].lower()
        assert "abertas" in result["message"].lower()


class TestListWindowsClosed:
    """Testes para listar janelas fechadas"""
    
    @patch('core.domains.sensor.get_state')
    def test_list_all_windows_closed(self, mock_get_state):
        """Deve indicar se todas as janelas estão fechadas"""
        mock_get_state.return_value = "off"
        
        intent = {"intent": "list_windows_closed"}
        result = handle(intent)
        
        assert "fechadas" in result["message"].lower()
    
    @patch('core.domains.sensor.get_state')
    def test_list_one_window_closed(self, mock_get_state):
        """Deve listar uma janela fechada"""
        def get_state_side_effect(entity_id):
            # banheiro sensor: binary_sensor.sonoff_1001879d3a
            if "sonoff" in entity_id:  # banheiro
                return "off"
            return "on"  # closet and quarto are open
        
        mock_get_state.side_effect = get_state_side_effect
        
        intent = {"intent": "list_windows_closed"}
        result = handle(intent)
        
        assert "banheiro" in result["message"].lower()
        assert "fechada" in result["message"].lower()
    
    @patch('core.domains.sensor.get_state')
    def test_list_multiple_windows_closed(self, mock_get_state):
        """Deve listar múltiplas janelas fechadas"""
        def get_state_side_effect(entity_id):
            # closet and banheiro are closed
            if "closet" in entity_id or "sonoff" in entity_id:
                return "off"
            return "on"  # quarto is open
        
        mock_get_state.side_effect = get_state_side_effect
        
        intent = {"intent": "list_windows_closed"}
        result = handle(intent)
        
        assert "closet" in result["message"].lower()
        assert "banheiro" in result["message"].lower()
        assert "fechadas" in result["message"].lower()



class TestParseWindowQueries:
    """Testes para parsing de queries de janelas"""
    
    def test_parse_janela_closet_aberta(self):
        """Deve parsear 'A janela do closet esta aberta?'"""
        from core.intent_parser import parse
        result = parse("A janela do closet esta aberta?")
        assert result["intent"] == "query_window"
        assert result["domain"] == "sensor"
        assert result["room"] == "closet"
        assert result["question_type"] == "open"
    
    def test_parse_janela_quarto_fechada(self):
        """Deve parsear 'A janela do quarto esta fechada?'"""
        from core.intent_parser import parse
        result = parse("A janela do quarto esta fechada?")
        assert result["intent"] == "query_window"
        assert result["domain"] == "sensor"
        assert result["room"] == "quarto"
        assert result["question_type"] == "closed"
    
    def test_parse_quais_janelas_abertas(self):
        """Deve parsear 'Quais janelas estão abertas?'"""
        from core.intent_parser import parse
        result = parse("Quais janelas estão abertas?")
        assert result["intent"] == "list_windows_open"
        assert result["domain"] == "sensor"
        assert result["state"] == "open"
    
    def test_parse_tem_alguma_janela_aberta(self):
        """Deve parsear 'Tem alguma janela aberta?'"""
        from core.intent_parser import parse
        result = parse("Tem alguma janela aberta?")
        assert result["intent"] == "list_windows_open"
        assert result["domain"] == "sensor"
    
    def test_parse_janela_banheiro_aberta(self):
        """Deve parsear 'A janela do banheiro esta aberta?'"""
        from core.intent_parser import parse
        result = parse("A janela do banheiro esta aberta?")
        assert result["intent"] == "query_window"
        assert result["room"] == "banheiro"
        assert result["question_type"] == "open"
