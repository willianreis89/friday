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


class TestFanFeature:
    """Testes para controle de ventilador"""
    
    def setup_method(self):
        """Limpa contexto antes de cada teste"""
        context.clear()
    
    @patch('core.domains.climate.call_service')
    def test_fan_on_quarto(self, mock_call):
        """Deve ligar ventilador do quarto"""
        mock_call.return_value = True
        
        intent = {"intent": "fan_on", "room": "quarto"}
        result = handle(intent)
        
        mock_call.assert_called_once_with("script", "ventilar_ar_lg_quarto", {})
        assert "ventilador" in result["message"].lower()
        assert "quarto" in result["message"].lower()
    
    @patch('core.domains.climate.call_service')
    def test_fan_off_closet(self, mock_call):
        """Deve desligar ventilador do closet"""
        mock_call.return_value = True
        
        intent = {"intent": "fan_off", "room": "closet"}
        result = handle(intent)
        
        mock_call.assert_called_once()
        assert "ventilador" in result["message"].lower()
        assert "closet" in result["message"].lower()
    
    def test_fan_on_sem_comodo(self):
        """Deve retornar erro se cômodo não especificado"""
        intent = {"intent": "fan_on", "room": None}
        result = handle(intent)
        
        assert "qual comodo" in result["message"].lower() or "quarto" in result["message"].lower()


class TestHeaterFeature:
    """Testes para controle de aquecedor"""
    
    def setup_method(self):
        """Limpa contexto antes de cada teste"""
        context.clear()
    
    @patch('core.domains.climate.call_service')
    def test_heater_on_quarto(self, mock_call):
        """Deve ligar aquecedor do quarto"""
        mock_call.return_value = True
        
        intent = {"intent": "heater_on", "room": "quarto"}
        result = handle(intent)
        
        mock_call.assert_called_once_with("script", "quente_ar_lg_quarto", {})
        assert "aquecedor" in result["message"].lower()
        assert "quarto" in result["message"].lower()
    
    @patch('core.domains.climate.call_service')
    def test_heater_off_quarto(self, mock_call):
        """Deve desligar aquecedor do quarto"""
        mock_call.return_value = True
        
        intent = {"intent": "heater_off", "room": "quarto"}
        result = handle(intent)
        
        mock_call.assert_called_once()
        assert "aquecedor" in result["message"].lower()
    
    def test_heater_on_closet_nao_disponivel(self):
        """Closet nao tem aquecedor, deve retornar erro"""
        intent = {"intent": "heater_on", "room": "closet"}
        result = handle(intent)
        
        assert "nao disponivel" in result["message"].lower() or "closet" in result["message"].lower()


class TestDisplayFeature:
    """Testes para controle de tela/display"""
    
    def setup_method(self):
        """Limpa contexto antes de cada teste"""
        context.clear()
    
    @patch('core.domains.climate.call_service')
    def test_display_off_quarto(self, mock_call):
        """Deve apagar tela do quarto via controle remoto"""
        mock_call.return_value = True
        
        intent = {"intent": "display_off", "room": "quarto"}
        result = handle(intent)
        
        # Deve chamar remote.send_command
        call_args = mock_call.call_args[0]
        assert call_args[0] == "remote"
        assert call_args[1] == "send_command"
        assert "tela" in result["message"].lower()
    
    def test_display_off_closet_nao_disponivel(self):
        """Closet nao tem controle remoto de display"""
        intent = {"intent": "display_off", "room": "closet"}
        result = handle(intent)
        
        assert "nao disponivel" in result["message"].lower() or "closet" in result["message"].lower()


class TestTemperatureFeature:
    """Testes para controle de temperatura"""
    
    def setup_method(self):
        """Limpa contexto antes de cada teste"""
        context.clear()
    
    @patch('core.domains.climate.call_service')
    def test_set_temperature_22_quarto(self, mock_call):
        """Deve definir temperatura para 22°C no quarto"""
        mock_call.return_value = True
        
        intent = {"intent": "set_temperature", "room": "quarto", "value": 22}
        result = handle(intent)
        
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        # call_service("input_number", "set_value", {"entity_id": ..., "value": 22})
        assert call_args[0][0] == "input_number"
        assert call_args[0][1] == "set_value"
        assert call_args[0][2]["value"] == 22
        assert "22" in result["message"]
    
    @patch('core.domains.climate.call_service')
    def test_set_temperature_18_closet(self, mock_call):
        """Deve definir temperatura minima (18°C)"""
        mock_call.return_value = True
        
        intent = {"intent": "set_temperature", "room": "closet", "value": 18}
        result = handle(intent)
        
        mock_call.assert_called_once()
        assert "18" in result["message"]
    
    @patch('core.domains.climate.call_service')
    def test_set_temperature_26_quarto(self, mock_call):
        """Deve definir temperatura maxima (26°C)"""
        mock_call.return_value = True
        
        intent = {"intent": "set_temperature", "room": "quarto", "value": 26}
        result = handle(intent)
        
        mock_call.assert_called_once()
        assert "26" in result["message"]
    
    def test_set_temperature_abaixo_minimo(self):
        """Deve rejeitar temperatura abaixo de 18°C"""
        intent = {"intent": "set_temperature", "room": "quarto", "value": 17}
        result = handle(intent)
        
        assert "18" in result["message"] and "26" in result["message"]
        assert "invalida" in result["message"].lower() or "entre" in result["message"].lower()
    
    def test_set_temperature_acima_maximo(self):
        """Deve rejeitar temperatura acima de 26°C"""
        intent = {"intent": "set_temperature", "room": "quarto", "value": 27}
        result = handle(intent)
        
        assert "18" in result["message"] and "26" in result["message"]
    
    def test_set_temperature_sem_valor(self):
        """Deve retornar erro se temperatura nao especificada"""
        intent = {"intent": "set_temperature", "room": "quarto", "value": None}
        result = handle(intent)
        
        assert "temperatura" in result["message"].lower()
    
    def test_set_temperature_sem_comodo(self):
        """Deve retornar erro se cômodo nao especificado"""
        intent = {"intent": "set_temperature", "room": None, "value": 22}
        result = handle(intent)
        
        assert "qual comodo" in result["message"].lower() or "quarto" in result["message"].lower()


class TestFanSpeedFeature:
    """Testes para controle de velocidade do ventilador"""
    
    def setup_method(self):
        """Limpa contexto antes de cada teste"""
        context.clear()
    
    @patch('core.domains.climate.call_service')
    def test_set_speed_1_quarto(self, mock_call):
        """Deve definir velocidade para 1"""
        mock_call.return_value = True
        
        intent = {"intent": "set_speed", "room": "quarto", "value": 1}
        result = handle(intent)
        
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        assert call_args[0][0] == "input_number"
        assert call_args[0][1] == "set_value"
        assert call_args[0][2]["value"] == 1
        assert "1" in result["message"]
    
    @patch('core.domains.climate.call_service')
    def test_set_speed_3_closet(self, mock_call):
        """Deve definir velocidade para 3 (máxima)"""
        mock_call.return_value = True
        
        intent = {"intent": "set_speed", "room": "closet", "value": 3}
        result = handle(intent)
        
        mock_call.assert_called_once()
        assert "3" in result["message"]
    
    def test_set_speed_zero(self):
        """Deve rejeitar velocidade 0"""
        intent = {"intent": "set_speed", "room": "quarto", "value": 0}
        result = handle(intent)
        
        assert "1" in result["message"] and "3" in result["message"]
    
    def test_set_speed_acima_maximo(self):
        """Deve rejeitar velocidade acima de 3"""
        intent = {"intent": "set_speed", "room": "quarto", "value": 4}
        result = handle(intent)
        
        assert "1" in result["message"] and "3" in result["message"]
    
    @patch('core.domains.climate.get_state')
    @patch('core.domains.climate.call_service')
    def test_increase_speed_de_1_para_2(self, mock_call, mock_get_state):
        """Deve aumentar velocidade de 1 para 2"""
        mock_get_state.return_value = "1"
        mock_call.return_value = True
        
        intent = {"intent": "increase_speed", "room": "quarto"}
        result = handle(intent)
        
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        assert call_args[0][0] == "input_number"
        assert call_args[0][1] == "set_value"
        assert call_args[0][2]["value"] == 2
        assert "2" in result["message"]
    
    @patch('core.domains.climate.get_state')
    @patch('core.domains.climate.call_service')
    def test_increase_speed_de_3_permanece_3(self, mock_call, mock_get_state):
        """Deve manter velocidade em 3 (máxima)"""
        mock_get_state.return_value = "3"
        mock_call.return_value = True
        
        intent = {"intent": "increase_speed", "room": "quarto"}
        result = handle(intent)
        
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        assert call_args[0][0] == "input_number"
        assert call_args[0][1] == "set_value"
        assert call_args[0][2]["value"] == 3
    
    @patch('core.domains.climate.get_state')
    @patch('core.domains.climate.call_service')
    def test_decrease_speed_de_3_para_2(self, mock_call, mock_get_state):
        """Deve diminuir velocidade de 3 para 2"""
        mock_get_state.return_value = "3"
        mock_call.return_value = True
        
        intent = {"intent": "decrease_speed", "room": "quarto"}
        result = handle(intent)
        
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        assert call_args[0][0] == "input_number"
        assert call_args[0][1] == "set_value"
        assert call_args[0][2]["value"] == 2
        assert "2" in result["message"]
    
    @patch('core.domains.climate.get_state')
    @patch('core.domains.climate.call_service')
    def test_decrease_speed_de_1_permanece_1(self, mock_call, mock_get_state):
        """Deve manter velocidade em 1 (mínima)"""
        mock_get_state.return_value = "1"
        mock_call.return_value = True
        
        intent = {"intent": "decrease_speed", "room": "quarto"}
        result = handle(intent)
        
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        assert call_args[0][0] == "input_number"
        assert call_args[0][1] == "set_value"
        assert call_args[0][2]["value"] == 1

