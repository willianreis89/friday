"""
Testes para core.dispatcher

Testa o roteamento de intents para dominios
"""
from unittest.mock import Mock, patch

import pytest

from core.context_manager import context
from core.dispatcher import dispatch


class TestDispatch:
    """Testes para funcao dispatch"""
    
    def setup_method(self):
        """Limpa contexto antes de cada teste"""
        context.clear()
    
    @patch('core.domains.light.handle')
    def test_dispatch_light_domain(self, mock_light_handle):
        """Deve rotear intent de luz para light.handle"""
        mock_light_handle.return_value = {"message": "Luz ligada"}
        
        intent = {"domain": "light", "intent": "on", "search": "sala"}
        result = dispatch(intent)
        
        mock_light_handle.assert_called_once_with(intent)
        assert result == {"message": "Luz ligada"}
    
    @patch('core.domains.climate.handle')
    def test_dispatch_climate_domain(self, mock_climate_handle):
        """Deve rotear intent de clima para climate.handle"""
        mock_climate_handle.return_value = {"message": "Ar ligado"}
        
        intent = {"domain": "climate", "intent": "on", "search": "quarto"}
        result = dispatch(intent)
        
        mock_climate_handle.assert_called_once_with(intent)
        assert result == {"message": "Ar ligado"}
    
    def test_dispatch_unknown_domain(self):
        """Deve retornar mensagem de erro para dominio desconhecido"""
        intent = {"domain": "unknown", "intent": "something"}
        result = dispatch(intent)
        
        assert "message" in result
        assert "repetir" in result["message"].lower() or "entendi" in result["message"].lower()
    
    def test_dispatch_none_domain(self):
        """Deve lidar com dominio None"""
        intent = {"domain": None, "intent": "on"}
        result = dispatch(intent)
        
        assert "message" in result
    
    @patch('core.domains.light.handle_confirmation')
    def test_dispatch_with_active_context_light(self, mock_confirmation):
        """Deve rotear para confirmacao quando contexto ativo (light)"""
        mock_confirmation.return_value = {"message": "Luz desligada"}
        
        # Define contexto ativo
        context.set({"domain": "light", "action": "off"})
        
        intent = {"text": "sala"}
        result = dispatch(intent)
        
        mock_confirmation.assert_called_once_with(intent)
        assert result == {"message": "Luz desligada"}
    
    @patch('core.domains.climate.handle_confirmation')
    def test_dispatch_with_active_context_climate(self, mock_confirmation):
        """Deve rotear para confirmacao quando contexto ativo (climate)"""
        mock_confirmation.return_value = {"message": "Ar desligado"}
        
        # Define contexto ativo
        context.set({"domain": "climate", "action": "off"})
        
        intent = {"text": "quarto"}
        result = dispatch(intent)
        
        mock_confirmation.assert_called_once_with(intent)
        assert result == {"message": "Ar desligado"}
    
    @patch('core.domains.light.handle')
    def test_dispatch_expired_context_routes_normally(self, mock_light_handle):
        """Deve rotear normalmente se contexto expirado"""
        mock_light_handle.return_value = {"message": "OK"}
        
        # Define contexto que expira imediatamente
        context.set({"domain": "light"}, ttl=0)
        
        import time
        time.sleep(0.1)
        
        intent = {"domain": "light", "intent": "on"}
        result = dispatch(intent)
        
        # Deve chamar handle normal, nao confirmation
        mock_light_handle.assert_called_once_with(intent)


class TestDispatchIntegration:
    """Testes de integracao entre dispatcher e dominios"""
    
    def setup_method(self):
        """Limpa contexto antes de cada teste"""
        context.clear()
    
    @patch('core.domains.light.call_service')
    @patch('core.domains.light.get_all_states')
    def test_dispatch_full_flow_light(self, mock_states, mock_call):
        """Teste de fluxo completo para luz"""
        mock_states.return_value = [
            {
                "entity_id": "light.sala",
                "state": "off",
                "attributes": {"friendly_name": "Luz Sala"}
            }
        ]
        mock_call.return_value = True
        
        intent = {
            "domain": "light",
            "intent": "on",
            "search": "luz sala"
        }
        
        result = dispatch(intent)
        
        assert "message" in result
        mock_call.assert_called_once()
