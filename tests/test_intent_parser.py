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
    
    def test_parse_ar_plural_on(self):
        """Deve detectar plural e retornar all_on para clima"""
        result = parse("ligar os dois ar")
        assert result["intent"] == "all_on"
        assert result["domain"] == "climate"
        
        result = parse("ligar os dois ar-condicionados")
        assert result["intent"] == "all_on"
        assert result["domain"] == "climate"
        
        result = parse("ligar arcondicionados")
        assert result["intent"] == "all_on"
        assert result["domain"] == "climate"
    
    def test_parse_ar_plural_off(self):
        """Deve detectar plural e retornar all_off para clima"""
        result = parse("desligar os dois ar")
        assert result["intent"] == "all_off"
        assert result["domain"] == "climate"
        
        result = parse("desligar todos ar-condicionados")
        assert result["intent"] == "all_off"
        assert result["domain"] == "climate"
    
    def test_parse_ar_sem_acao(self):
        """Deve retornar erro se ar sem acao definida"""
        result = parse("ar do quarto")
        assert result["intent"] == "error"
        assert result["domain"] == "climate"


class TestParseClimateFan:
    """Testes para parsing de comandos de ventilador do ar"""
    
    def test_parse_fan_on_quarto(self):
        """Deve parsear ligar ventilador do quarto"""
        result = parse("ligar ventilador do ar do quarto")
        assert result["intent"] == "fan_on"
        assert result["domain"] == "climate"
        assert result["room"] == "quarto"
    
    def test_parse_fan_off_closet(self):
        """Deve parsear desligar ventilador do closet"""
        result = parse("desligar ventilador closet")
        assert result["intent"] == "fan_off"
        assert result["domain"] == "climate"
        assert result["room"] == "closet"
    
    def test_parse_fan_on_sem_comodo(self):
        """Deve parsear fan_on mesmo sem comodo especificado"""
        result = parse("ligar ventilador")
        assert result["intent"] == "fan_on"
        assert result["domain"] == "climate"


class TestParseClimateHeater:
    """Testes para parsing de comandos de aquecedor"""
    
    def test_parse_heater_on_quarto(self):
        """Deve parsear ligar aquecedor"""
        result = parse("ligar aquecedor quarto")
        assert result["intent"] == "heater_on"
        assert result["domain"] == "climate"
        assert result["room"] == "quarto"
    
    def test_parse_heater_off_quarto(self):
        """Deve parsear desligar aquecedor"""
        result = parse("desligar aquecimento do ar do quarto")
        assert result["intent"] == "heater_off"
        assert result["domain"] == "climate"
        assert result["room"] == "quarto"


class TestParseClimateTemperature:
    """Testes para parsing de comandos de temperatura"""
    
    def test_parse_set_temperature_22(self):
        """Deve parsear definir temperatura para 22°C"""
        result = parse("colocar temperatura 22 graus")
        assert result["intent"] == "set_temperature"
        assert result["domain"] == "climate"
        assert result["value"] == 22
    
    def test_parse_set_temperature_18(self):
        """Deve parsear definir temperatura minima"""
        result = parse("definir temperatura 18")
        assert result["intent"] == "set_temperature"
        assert result["value"] == 18
    
    def test_parse_set_temperature_26(self):
        """Deve parsear definir temperatura maxima"""
        result = parse("temperatura 26 graus quarto")
        assert result["intent"] == "set_temperature"
        assert result["value"] == 26
        assert result["room"] == "quarto"
    
    def test_parse_temperature_range(self):
        """Deve parsear range de temperatura (18-26)"""
        result = parse("colocar temperatura entre 18 e 26 graus")
        assert result["intent"] == "set_temperature"
        # Deve extrair o primeiro valor do range
        assert result["value"] == 18
    
    def test_parse_temperature_sem_valor(self):
        """Deve retornar erro se temperatura sem valor"""
        result = parse("colocar temperatura")
        assert result["intent"] == "error"
        assert "temperatura" in result["response"].lower()


class TestParseClimateSpeed:
    """Testes para parsing de comandos de velocidade do ventilador"""
    
    def test_parse_set_speed_1(self):
        """Deve parsear definir velocidade para 1"""
        result = parse("velocidade 1 quarto")
        assert result["intent"] == "set_speed"
        assert result["domain"] == "climate"
        assert result["value"] == 1
        assert result["room"] == "quarto"
    
    def test_parse_set_speed_3(self):
        """Deve parsear definir velocidade para 3"""
        result = parse("colocar velocidade 3 no ar")
        assert result["intent"] == "set_speed"
        assert result["value"] == 3
    
    def test_parse_increase_speed(self):
        """Deve parsear aumentar velocidade"""
        result = parse("aumentar velocidade do ar quarto")
        assert result["intent"] == "increase_speed"
        assert result["domain"] == "climate"
        assert result["room"] == "quarto"
    
    def test_parse_increase_speed_subir(self):
        """Deve parsear subir velocidade (alias)"""
        result = parse("subir velocidade closet")
        assert result["intent"] == "increase_speed"
        assert result["room"] == "closet"
    
    def test_parse_decrease_speed(self):
        """Deve parsear diminuir velocidade"""
        result = parse("abaixar velocidade quarto")
        assert result["intent"] == "decrease_speed"
        assert result["room"] == "quarto"
    
    def test_parse_decrease_speed_reduzir(self):
        """Deve parsear reduzir velocidade (alias)"""
        result = parse("reduzir velocidade do ar")
        assert result["intent"] == "decrease_speed"


class TestParseClimateDisplay:
    """Testes para parsing de comandos de display/tela"""
    
    def test_parse_display_off_quarto(self):
        """Deve parsear desligar tela do quarto"""
        result = parse("apagar tela do ar quarto")
        assert result["intent"] == "display_off"
        assert result["domain"] == "climate"
        assert result["room"] == "quarto"
    
    def test_parse_display_off_closet(self):
        """Deve parsear desligar display do closet"""
        result = parse("desligar display closet")
        assert result["intent"] == "display_off"
        assert result["room"] == "closet"
    
    def test_parse_display_off_com_scoreboard(self):
        """Deve parsear desligar scoreboard"""
        result = parse("desligar scoreboard quarto")
        assert result["intent"] == "display_off"
        assert result["room"] == "quarto"


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


class TestParseSensorQueries:
    """Testes para parsing de queries de sensor"""
    
    def test_parse_query_temperatura_quarto(self):
        """Deve parsear 'Qual a temperatura do quarto?'"""
        result = parse("Qual a temperatura do quarto?")
        assert result["intent"] == "query_sensor"
        assert result["domain"] == "sensor"
        assert result["room"] == "quarto"
    
    def test_parse_query_temperatura_closet(self):
        """Deve parsear 'Qual a temperatura do closet?'"""
        result = parse("Qual a temperatura do closet?")
        assert result["intent"] == "query_sensor"
        assert result["domain"] == "sensor"
        assert result["room"] == "closet"
    
    def test_parse_query_externa(self):
        """Deve parsear queries com 'externa' ou 'sacada'"""
        result = parse("Qual a temperatura da sacada?")
        assert result["intent"] == "query_sensor"
        assert result["domain"] == "sensor"
        assert result["room"] == "externa"
    
    def test_parse_query_umidade_quarto(self):
        """Deve parsear query de umidade"""
        result = parse("Qual a umidade do quarto?")
        assert result["intent"] == "query_sensor"
        assert result["domain"] == "sensor"
        assert result["room"] == "quarto"


class TestParseSensorComparisons:
    """Testes para parsing de comparações de sensores"""
    
    def test_parse_compare_qual_mais_quente(self):
        """Deve parsear 'Qual ambiente está mais quente?'"""
        result = parse("Qual ambiente está mais quente?")
        assert result["intent"] == "compare_all_sensors"
        assert result["domain"] == "sensor"
        assert result["sensor_type"] == "temperature"
        assert result["comparison_type"] == "highest"
    
    def test_parse_compare_quarto_ou_closet(self):
        """Deve parsear 'Onde está mais frio, quarto ou closet?'"""
        result = parse("Onde está mais frio, quarto ou closet?")
        assert result["intent"] == "compare_sensors"
        assert result["domain"] == "sensor"
        assert result["sensor_type"] == "temperature"
        assert "quarto" in result["rooms"]
        assert "closet" in result["rooms"]
    
    def test_parse_compare_quarto_vs_externa(self):
        """Deve parsear comparação entre quarto e externa"""
        result = parse("Qual está mais quente, quarto ou sacada?")
        assert result["intent"] == "compare_sensors"
        assert result["domain"] == "sensor"
        assert result["sensor_type"] == "temperature"
        assert "quarto" in result["rooms"]
        assert "externa" in result["rooms"]
    
    def test_parse_compare_temperatura_mais_alta(self):
        """Deve parsear 'Qual a temperatura mais alta da casa?'"""
        result = parse("Qual a temperatura mais alta da casa?")
        assert result["intent"] == "compare_all_sensors"
        assert result["domain"] == "sensor"
        assert result["sensor_type"] == "temperature"
        assert result["comparison_type"] == "highest"
    
    def test_parse_compare_qual_mais_frio(self):
        """Deve parsear 'Qual está mais frio?'"""
        result = parse("Qual está mais frio?")
        assert result["intent"] == "compare_all_sensors"
        assert result["domain"] == "sensor"
        assert result["sensor_type"] == "temperature"
        assert result["comparison_type"] == "lowest"
