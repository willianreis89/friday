"""
Testes para core.domains.light

Testa handlers de comandos de luz
"""
from unittest.mock import Mock, patch

import pytest

from core.context_manager import context
from core.domains.light import (find_light_entities, handle, handle_single,
                                normalize_name)


class TestNormalizeName:
    """Testes para normalize_name"""
    
    def test_normalize_lowercase(self):
        """Deve converter para minusculas"""
        assert normalize_name("LUZ SALA") == "luz sala"
    
    def test_normalize_remove_prepositions(self):
        """Deve remover preposicoes"""
        assert normalize_name("luz do quarto") == "luz quarto"
        assert normalize_name("luz da sala") == "luz sala"
    
    def test_normalize_multiple_spaces(self):
        """Deve normalizar espacos multiplos"""
        assert normalize_name("luz   da    sala") == "luz sala"


class TestFindLightEntities:
    """Testes para find_light_entities"""
    
    @patch('core.domains.light.get_all_lights')
    def test_find_light_entities_single_match(self, mock_get_lights):
        """Deve encontrar entidade que corresponde"""
        mock_get_lights.return_value = [
            {
                "entity_id": "light.sala",
                "attributes": {"friendly_name": "Luz da Sala"}
            },
            {
                "entity_id": "light.quarto",
                "attributes": {"friendly_name": "Luz do Quarto"}
            }
        ]
        
        result = find_light_entities("luz sala")
        
        assert "light.sala" in result
        assert len(result) == 1
    
    @patch('core.domains.light.get_all_lights')
    def test_find_light_entities_multiple_matches(self, mock_get_lights):
        """Deve encontrar multiplas entidades"""
        mock_get_lights.return_value = [
            {
                "entity_id": "light.led_quarto_1",
                "attributes": {"friendly_name": "LED Quarto 1"}
            },
            {
                "entity_id": "light.led_quarto_2",
                "attributes": {"friendly_name": "LED Quarto 2"}
            }
        ]
        
        result = find_light_entities("led quarto")
        
        assert len(result) == 2
    
    @patch('core.domains.light.get_all_lights')
    def test_find_light_entities_no_match(self, mock_get_lights):
        """Deve retornar lista vazia se nao encontrar"""
        mock_get_lights.return_value = [
            {
                "entity_id": "light.sala",
                "attributes": {"friendly_name": "Luz da Sala"}
            }
        ]
        
        result = find_light_entities("cozinha")
        
        assert result == []


class TestHandle:
    """Testes para funcao handle principal"""
    
    @patch('core.domains.light.handle_single')
    def test_handle_routes_to_single(self, mock_single):
        """Deve rotear para handle_single quando tem search"""
        mock_single.return_value = {"message": "OK"}
        
        intent = {"intent": "on", "search": "sala"}
        result = handle(intent)
        
        mock_single.assert_called_once_with(intent)
    
    @patch('core.domains.light.handle_all')
    def test_handle_routes_to_all_on(self, mock_all):
        """Deve rotear para handle_all quando all_on"""
        mock_all.return_value = {"message": "OK"}
        
        intent = {"intent": "all_on"}
        result = handle(intent)
        
        mock_all.assert_called_once_with(intent)
    
    @patch('core.domains.light.handle_all')
    def test_handle_routes_to_all_off(self, mock_all):
        """Deve rotear para handle_all quando all_off"""
        mock_all.return_value = {"message": "OK"}
        
        intent = {"intent": "all_off"}
        result = handle(intent)
        
        mock_all.assert_called_once_with(intent)
    
    @patch('core.domains.light.handle_multi')
    def test_handle_routes_to_multi(self, mock_multi):
        """Deve rotear para handle_multi"""
        mock_multi.return_value = {"message": "OK"}
        
        intent = {"intent": "multi", "text": "ligar sala e desligar quarto"}
        result = handle(intent)
        
        mock_multi.assert_called_once_with(intent)
    
    def test_handle_unknown_intent(self):
        """Deve retornar erro para intent desconhecida"""
        intent = {"intent": "unknown"}
        result = handle(intent)
        
        assert "message" in result
        assert "entendi" in result["message"].lower()


class TestHandleSingle:
    """Testes para handle_single"""
    
    def setup_method(self):
        """Limpa contexto antes de cada teste"""
        context.clear()
    
    @patch('core.domains.light.call_service')
    @patch('core.domains.light.find_light_entities')
    def test_handle_single_light_on(self, mock_find, mock_call):
        """Deve ligar luz encontrada"""
        mock_find.return_value = ["light.sala"]
        mock_call.return_value = True
        
        intent = {"intent": "on", "search": "sala"}
        result = handle_single(intent)
        
        mock_call.assert_called_once_with("light", "turn_on", {"entity_id": ["light.sala"]})
        assert "ligada" in result["message"].lower()
    
    @patch('core.domains.light.call_service')
    @patch('core.domains.light.find_light_entities')
    def test_handle_single_light_off(self, mock_find, mock_call):
        """Deve desligar luz encontrada"""
        mock_find.return_value = ["light.quarto"]
        mock_call.return_value = True
        
        intent = {"intent": "off", "search": "quarto"}
        result = handle_single(intent)
        
        mock_call.assert_called_once_with("light", "turn_off", {"entity_id": ["light.quarto"]})
        assert "desligada" in result["message"].lower()
    
    @patch('core.domains.light.find_light_entities')
    def test_handle_single_light_not_found(self, mock_find):
        """Deve retornar erro se luz nao encontrada"""
        mock_find.return_value = []
        
        intent = {"intent": "on", "search": "inexistente"}
        result = handle_single(intent)
        
        assert "message" in result
        assert "encontrei" in result["message"].lower()
    
    @patch('core.domains.light.get_lights_on')
    def test_handle_single_generic_off_no_lights(self, mock_lights_on):
        """'desligar luz' sem nenhuma luz ligada"""
        mock_lights_on.return_value = []
        
        intent = {"intent": "off", "search": "luz"}
        result = handle_single(intent)
        
        assert "nenhuma" in result["message"].lower()
    
    @patch('core.domains.light.call_service')
    @patch('core.domains.light.get_lights_on')
    def test_handle_single_generic_off_one_light(self, mock_lights_on, mock_call):
        """'desligar luz' com uma luz ligada deve desligar"""
        mock_lights_on.return_value = [
            {"entity_id": "light.sala", "state": "on"}
        ]
        mock_call.return_value = True
        
        intent = {"intent": "off", "search": "luz"}
        result = handle_single(intent)
        
        mock_call.assert_called_once()
        assert "desligada" in result["message"].lower()
    
    @patch('core.domains.light.get_lights_on')
    def test_handle_single_generic_off_multiple_lights_creates_context(self, mock_lights_on):
        """'desligar luz' com multiplas luzes deve criar contexto"""
        mock_lights_on.return_value = [
            {"entity_id": "light.sala", "state": "on"},
            {"entity_id": "light.quarto", "state": "on"}
        ]
        
        intent = {"intent": "off", "search": "luz"}
        result = handle_single(intent)
        
        assert context.valid()
        assert "mais de uma" in result["message"].lower()
        assert "qual" in result["message"].lower()


class TestHandleSingleMultipleEntities:
    """Testes para handle_single com multiplas entidades"""
    
    @patch('core.domains.light.call_service')
    @patch('core.domains.light.find_light_entities')
    def test_handle_single_multiple_entities(self, mock_find, mock_call):
        """Deve ligar/desligar multiplas entidades de uma vez"""
        mock_find.return_value = ["light.led1", "light.led2"]
        mock_call.return_value = True
        
        intent = {"intent": "on", "search": "led"}
        result = handle_single(intent)
        
        # Deve enviar lista com ambas entidades
        call_args = mock_call.call_args[0]
        assert call_args[2]["entity_id"] == ["light.led1", "light.led2"]
