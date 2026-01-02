"""
Testes para core.intent_parser

Testa a normalizacao de texto e parsing de intents
"""
import pytest

from core.intent_parser import normalize, parse


class TestNormalize:
    """Testes para a funcao normalize"""
    
    def test_normalize_remove_acentos(self):
        """Deve remover acentos e caracteres especiais"""
        assert normalize("ligar lâmpada") == "ligar lampada"
        assert normalize("desligar árêâ") == "desligar area"
    
    def test_normalize_lowercase(self):
        """Deve converter para minusculas"""
        assert normalize("LIGAR LUZ") == "ligar luz"
        assert normalize("Desligar Ar") == "desligar ar"
    
    def test_normalize_remove_stopwords(self):
        """Deve remover stopwords"""
        assert normalize("ligar a luz da sala") == "ligar luz sala"
        assert normalize("desligar o ar do quarto") == "desligar ar quarto"
    
    def test_normalize_empty_string(self):
        """Deve lidar com string vazia"""
        assert normalize("") == ""
    
    def test_normalize_only_stopwords(self):
        """Deve retornar vazio se apenas stopwords"""
        assert normalize("do da de") == ""


class TestParseLights:
    """Testes para parsing de comandos de luz"""
    
    def test_parse_ligar_luz_simples(self):
        """Deve parsear comando de ligar luz"""
        result = parse("ligar luz da sala")
        assert result["intent"] == "on"
        assert result["domain"] == "light"
        assert "sala" in result["search"]
    
    def test_parse_desligar_luz_simples(self):
        """Deve parsear comando de desligar luz"""
        result = parse("desligar luz do quarto")
        assert result["intent"] == "off"
        assert result["domain"] == "light"
        assert "quarto" in result["search"]
    
    def test_parse_acender_sinonimo(self):
        """Deve reconhecer 'acender' como sinonimo de ligar"""
        result = parse("acender luz da cozinha")
        assert result["intent"] == "on"
        assert result["domain"] == "light"
    
    def test_parse_apagar_sinonimo(self):
        """Deve reconhecer 'apagar' como sinonimo de desligar"""
        result = parse("apagar luz do banheiro")
        assert result["intent"] == "off"
        assert result["domain"] == "light"
    
    def test_parse_todas_as_luzes_on(self):
        """Deve parsear comando para ligar todas as luzes"""
        result = parse("ligar todas as luzes")
        assert result["intent"] == "all_on"
        assert result["domain"] == "light"
    
    def test_parse_todas_as_luzes_off(self):
        """Deve parsear comando para desligar todas as luzes"""
        result = parse("desligar todas as luzes")
        assert result["intent"] == "all_off"
        assert result["domain"] == "light"
    
    def test_parse_multi_comando(self):
        """Deve detectar comando multiplo com 'e'"""
        result = parse("ligar luz da sala e desligar luz do quarto")
        assert result["intent"] == "multi"
        assert result["domain"] == "light"
    
    def test_parse_led(self):
        """Deve reconhecer comandos com LED"""
        result = parse("ligar led da mesa")
        assert result["intent"] == "on"
        assert result["domain"] == "light"
        assert "led" in result["search"] or "mesa" in result["search"]


class TestParseClimate:
    """Testes para parsing de comandos de ar-condicionado"""
    
    def test_parse_ligar_ar_com_comodo(self):
        """Deve parsear comando de ligar ar com comodo"""
        result = parse("ligar ar do quarto")
        assert result["intent"] == "on"
        assert result["domain"] == "climate"
        assert "quarto" in result["search"]
    
    def test_parse_desligar_ar_com_comodo(self):
        """Deve parsear comando de desligar ar com comodo"""
        result = parse("desligar ar do closet")
        assert result["intent"] == "off"
        assert result["domain"] == "climate"
        assert "closet" in result["search"]
    
    def test_parse_ar_condicionado_completo(self):
        """Deve reconhecer 'ar condicionado' completo"""
        result = parse("ligar ar condicionado do quarto")
        assert result["intent"] == "on"
        assert result["domain"] == "climate"
    
    def test_parse_ar_generico_on(self):
        """Deve parsear comando generico de ligar ar"""
        result = parse("ligar ar")
        assert result["intent"] == "on"
        assert result["domain"] == "climate"
    
    def test_parse_ar_generico_off(self):
        """Deve parsear comando generico de desligar ar"""
        result = parse("desligar ar")
        assert result["intent"] == "off"
        assert result["domain"] == "climate"
    
    def test_parse_ar_sem_acao(self):
        """Deve retornar erro se ar sem acao definida"""
        result = parse("ar do quarto")
        assert result["intent"] == "error"
        assert result["domain"] == "climate"


class TestParseEdgeCases:
    """Testes para casos extremos"""
    
    def test_parse_comando_vazio(self):
        """Deve lidar com comando vazio"""
        result = parse("")
        # Deve retornar algo, mesmo que seja erro
        assert isinstance(result, dict)
    
    def test_parse_comando_desconhecido(self):
        """Deve lidar com comando nao reconhecido"""
        result = parse("abrir janela")
        # Pode retornar None ou dict com erro
        assert result is None or isinstance(result, dict)
    
    def test_parse_apenas_acao_sem_alvo(self):
        """Deve lidar com acao sem alvo especifico"""
        result = parse("ligar luz")
        assert result["intent"] == "on"
        assert result["domain"] == "light"
        # search deve ter "luz" como default
        assert "luz" in result["search"]
