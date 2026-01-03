"""
Testes para core.domains.climate

Testa handlers de comandos de ar-condicionado
"""
from unittest.mock import Mock, patch

import pytest

from core.context_manager import context
from core.domains.climate import handle, is_generic_ar, match_room


class TestMatchRoom:
    """Testes para match_room"""
    
    def test_match_room_quarto(self):
        """Deve identificar quarto"""
        assert match_room("quarto") == "quarto"
        assert match_room("ar do quarto") == "quarto"
        assert match_room("ar condicionado quarto") == "quarto"
    
    def test_match_room_closet(self):
        """Deve identificar closet"""
        assert match_room("closet") == "closet"
        assert match_room("ar do closet") == "closet"
    
    def test_match_room_not_found(self):
        """Deve retornar None se comodo nao identificado"""
        assert match_room("sala") is None
        assert match_room("cozinha") is None
        assert match_room("") is None


class TestIsGenericAr:
    """Testes para is_generic_ar"""
    
    def test_is_generic_ar_true(self):
        """Deve identificar comandos genericos de ar"""
        assert is_generic_ar("ar") is True
        assert is_generic_ar("ar condicionado") is True
        assert is_generic_ar("ar-condicionado") is True
        assert is_generic_ar("") is True
    
    def test_is_generic_ar_false(self):
        """Deve retornar False para comandos especificos"""
        assert is_generic_ar("ar do quarto") is False
        assert is_generic_ar("quarto") is False


class TestHandle:
    """Testes para funcao handle principal"""
    
    def setup_method(self):
        """Limpa contexto antes de cada teste"""
        context.clear()
    
    @patch('core.domains.climate.call_service')
    def test_handle_ligar_ar_com_comodo(self, mock_call):
        """Deve ligar ar de comodo especifico"""
        mock_call.return_value = True
        
        intent = {"intent": "on", "search": "ar quarto"}
        result = handle(intent)
        
        mock_call.assert_called_once()
        assert "quarto" in result["message"].lower()
        assert "ligado" in result["message"].lower()
    
    @patch('core.domains.climate.call_service')
    def test_handle_desligar_ar_com_comodo(self, mock_call):
        """Deve desligar ar de comodo especifico"""
        mock_call.return_value = True
        
        intent = {"intent": "off", "search": "ar closet"}
        result = handle(intent)
        
        mock_call.assert_called_once()
        assert "closet" in result["message"].lower()
        assert "desligado" in result["message"].lower()
    
    @patch('core.domains.climate.call_service')
    def test_handle_usa_script_correto_on(self, mock_call):
        """Deve usar script correto para ligar"""
        mock_call.return_value = True
        
        intent = {"intent": "on", "search": "quarto"}
        handle(intent)
        
        call_args = mock_call.call_args[0]
        assert call_args[0] == "script"
        assert "gelar_ar_lg_quarto" in call_args[1]
    
    @patch('core.domains.climate.call_service')
    def test_handle_usa_script_correto_off(self, mock_call):
        """Deve usar script correto para desligar"""
        mock_call.return_value = True
        
        intent = {"intent": "off", "search": "closet"}
        handle(intent)
        
        call_args = mock_call.call_args[0]
        assert call_args[0] == "script"
        assert "desligar_ar_lg_closet" in call_args[1]
    
    @patch('core.domains.climate.call_service')
    def test_handle_all_on(self, mock_call):
        """Deve ligar todos os ares-condicionados"""
        mock_call.return_value = True
        
        intent = {"intent": "all_on"}
        result = handle(intent)
        
        # Deve chamar call_service 2 vezes (quarto e closet)
        assert mock_call.call_count == 2
        assert "todos" in result["message"].lower()
        assert "ligados" in result["message"].lower()
    
    @patch('core.domains.climate.call_service')
    def test_handle_all_off(self, mock_call):
        """Deve desligar todos os ares-condicionados"""
        mock_call.return_value = True
        
        intent = {"intent": "all_off"}
        result = handle(intent)
        
        # Deve chamar call_service 2 vezes (quarto e closet)
        assert mock_call.call_count == 2
        assert "todos" in result["message"].lower()
        assert "desligados" in result["message"].lower()
    
    @patch('core.domains.climate.is_on')
    def test_handle_generic_off_nenhum_ligado(self, mock_is_on):
        """'desligar ar' sem nenhum ar ligado"""
        mock_is_on.return_value = False
        
        intent = {"intent": "off", "search": "ar"}
        result = handle(intent)
        
        assert "nenhum" in result["message"].lower()
    
    @patch('core.domains.climate.call_service')
    @patch('core.domains.climate.is_on')
    def test_handle_generic_off_um_ligado(self, mock_is_on, mock_call):
        """'desligar ar' com um ar ligado deve desligar"""
        mock_is_on.side_effect = [True, False]  # quarto ligado, closet desligado
        mock_call.return_value = True
        
        intent = {"intent": "off", "search": "ar"}
        result = handle(intent)
        
        mock_call.assert_called_once()
        assert "desligado" in result["message"].lower()
    
    @patch('core.domains.climate.is_on')
    def test_handle_generic_off_multiplos_ligados_cria_contexto(self, mock_is_on):
        """'desligar ar' com multiplos ares ligados deve criar contexto"""
        mock_is_on.return_value = True  # ambos ligados
        
        intent = {"intent": "off", "search": "ar"}
        result = handle(intent)
        
        assert context.valid()
        assert "mais de um" in result["message"].lower()
        assert "qual" in result["message"].lower()
    
    def test_handle_comando_desconhecido(self):
        """Deve retornar erro para comando nao compreendido"""
        intent = {"intent": "off", "search": "sala"}
        result = handle(intent)
        
        assert "message" in result
        assert "entendi" in result["message"].lower()


class TestHandleConfirmation:
    """Testes para handle_confirmation"""
    
    def setup_method(self):
        """Limpa contexto antes de cada teste"""
        context.clear()
    
    @patch('core.domains.climate.call_service')
    def test_handle_confirmation_single_room(self, mock_call):
        """Deve desligar ar do comodo especificado"""
        mock_call.return_value = True
        
        # Simula contexto de confirmacao
        context.set({
            "domain": "climate",
            "candidates": [
                {"room": "quarto", "script": "script.desligar_ar_lg_quarto"},
                {"room": "closet", "script": "script.desligar_ar_lg_closet"}
            ]
        })
        
        from core.domains.climate import handle_confirmation
        
        intent = {"text": "quarto"}
        result = handle_confirmation(intent)
        
        mock_call.assert_called_once()
        # Contexto deve ser limpo
        assert not context.valid()
    
    @patch('core.domains.climate.call_service')
    def test_handle_confirmation_todos(self, mock_call):
        """Deve desligar todos os ares quando 'todos'"""
        mock_call.return_value = True
        
        context.set({
            "domain": "climate",
            "candidates": [
                {"room": "quarto", "script": "script.desligar_ar_lg_quarto"},
                {"room": "closet", "script": "script.desligar_ar_lg_closet"}
            ]
        })
        
        from core.domains.climate import handle_confirmation
        
        intent = {"text": "todos"}
        result = handle_confirmation(intent)
        
        # Deve chamar call_service 2 vezes
        assert mock_call.call_count == 2
        assert "todos" in result["message"].lower()
    
    def test_handle_confirmation_invalid_context(self):
        """Deve retornar erro se contexto invalido"""
        context.set({"domain": "light"})  # contexto errado
        
        from core.domains.climate import handle_confirmation
        
        intent = {"text": "quarto"}
        result = handle_confirmation(intent)
        
        assert "invalida" in result["message"].lower() or "message" in result
    
    def test_handle_confirmation_unrecognized_response(self):
        """Deve retornar erro se resposta nao reconhecida"""
        context.set({
            "domain": "climate",
            "candidates": [
                {"room": "quarto", "script": "script.desligar_ar_lg_quarto"}
            ]
        })
        
        from core.domains.climate import handle_confirmation
        
        intent = {"text": "xyz"}
        result = handle_confirmation(intent)
        
        assert "message" in result
        assert not context.valid()  # contexto limpo mesmo com erro
    
    @patch('core.domains.climate.call_service')
    def test_handle_confirmation_specific_room_from_multiple(self, mock_call):
        """Deve desligar apenas o ar especificado quando ha multiplos"""
        mock_call.return_value = True
        
        # Simula contexto de confirmacao com 2 ares ligados
        context.set({
            "domain": "climate",
            "action": "off",
            "candidates": [
                {"room": "quarto", "script": "script.desligar_ar_lg_quarto"},
                {"room": "closet", "script": "script.desligar_ar_lg_closet"}
            ]
        })
        
        from core.domains.climate import handle_confirmation
        
        # Usuario responde "closet"
        intent = {"text": "closet"}
        result = handle_confirmation(intent)
        
        # Deve chamar call_service apenas 1 vez com o script correto
        mock_call.assert_called_once_with("script", "desligar_ar_lg_closet", {})
        assert "closet" in result["message"].lower()
        assert "desligado" in result["message"].lower()
        # Contexto deve ser limpo
        assert not context.valid()
