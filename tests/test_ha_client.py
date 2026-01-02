"""
Testes para core.ha_client

Testa integracao com Home Assistant API usando mocks
"""
from unittest.mock import Mock, patch

import pytest
import requests

from core.ha_client import call_service, get_all_states, get_state


class TestCallService:
    """Testes para call_service"""
    
    @patch('core.ha_client.requests.post')
    def test_call_service_success(self, mock_post):
        """Deve chamar servico com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = call_service("light", "turn_on", {"entity_id": "light.sala"})
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('core.ha_client.requests.post')
    def test_call_service_with_correct_url(self, mock_post):
        """Deve construir URL corretamente"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        call_service("light", "turn_on", {"entity_id": "light.sala"})
        
        call_args = mock_post.call_args
        assert "/api/services/light/turn_on" in call_args[1]['url'] or "/api/services/light/turn_on" in call_args[0][0]
    
    @patch('core.ha_client.requests.post')
    def test_call_service_timeout(self, mock_post):
        """Deve tratar timeout"""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(requests.exceptions.Timeout):
            call_service("light", "turn_on", {"entity_id": "light.sala"})
    
    @patch('core.ha_client.requests.post')
    def test_call_service_request_exception(self, mock_post):
        """Deve tratar erros de requisicao"""
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        
        with pytest.raises(requests.exceptions.RequestException):
            call_service("light", "turn_on", {"entity_id": "light.sala"})
    
    @patch('core.ha_client.requests.post')
    def test_call_service_http_error(self, mock_post):
        """Deve tratar erro HTTP"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
        mock_post.return_value = mock_response
        
        with pytest.raises(requests.exceptions.HTTPError):
            call_service("light", "turn_on", {"entity_id": "light.sala"})


class TestGetAllStates:
    """Testes para get_all_states"""
    
    @patch('core.ha_client.requests.get')
    def test_get_all_states_success(self, mock_get):
        """Deve retornar lista de estados"""
        mock_states = [
            {"entity_id": "light.sala", "state": "on"},
            {"entity_id": "light.quarto", "state": "off"}
        ]
        mock_response = Mock()
        mock_response.json.return_value = mock_states
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_all_states()
        
        assert len(result) == 2
        assert result[0]["entity_id"] == "light.sala"
    
    @patch('core.ha_client.requests.get')
    def test_get_all_states_empty(self, mock_get):
        """Deve retornar lista vazia se nao houver estados"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = get_all_states()
        
        assert result == []
    
    @patch('core.ha_client.requests.get')
    def test_get_all_states_timeout(self, mock_get):
        """Deve tratar timeout"""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(requests.exceptions.Timeout):
            get_all_states()
    
    @patch('core.ha_client.requests.get')
    def test_get_all_states_request_exception(self, mock_get):
        """Deve tratar erro de requisicao"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with pytest.raises(requests.exceptions.RequestException):
            get_all_states()


class TestGetState:
    """Testes para get_state"""
    
    @patch('core.ha_client.get_all_states')
    def test_get_state_found(self, mock_get_all):
        """Deve retornar estado quando entidade existe"""
        mock_get_all.return_value = [
            {"entity_id": "light.sala", "state": "on"},
            {"entity_id": "light.quarto", "state": "off"}
        ]
        
        result = get_state("light.sala")
        
        assert result == "on"
    
    @patch('core.ha_client.get_all_states')
    def test_get_state_not_found(self, mock_get_all):
        """Deve retornar None quando entidade nao existe"""
        mock_get_all.return_value = [
            {"entity_id": "light.sala", "state": "on"}
        ]
        
        result = get_state("light.inexistente")
        
        assert result is None
    
    @patch('core.ha_client.get_all_states')
    def test_get_state_empty_list(self, mock_get_all):
        """Deve retornar None quando lista vazia"""
        mock_get_all.return_value = []
        
        result = get_state("light.qualquer")
        
        assert result is None
