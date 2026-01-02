"""
==============================================================
EXEMPLO DE SAIDA DE LOGS DO FRIDAY
==============================================================

Este arquivo mostra como os logs aparecem durante a execução.
Os logs reais são salvos em: logs/friday_YYYYMMDD.log
==============================================================
"""

# Exemplo 1: Comando simples
"""
2026-01-02 14:30:15 | INFO     | stt.server          | ======================================================================
2026-01-02 14:30:15 | INFO     | stt.server          | COMANDO: 'ligar luz da sala'
2026-01-02 14:30:15 | DEBUG    | core.intent_parser  | Normalizado: 'ligar luz da sala' -> 'ligar luz sala'
2026-01-02 14:30:15 | INFO     | stt.server          | Intent parseada: on | Domain: light
2026-01-02 14:30:15 | INFO     | core.dispatcher     | Despachando: light.on
2026-01-02 14:30:15 | INFO     | core.domains.light  | Processando light.on
2026-01-02 14:30:15 | DEBUG    | core.domains.light  | Busca 'luz sala': 1 luz(es) encontrada(s)
2026-01-02 14:30:15 | DEBUG    | core.ha_client      | Chamando servico: light.turn_on | Data: {'entity_id': ['light.sala']}
2026-01-02 14:30:15 | INFO     | core.ha_client      | API [POST] http://172.30.156.7:8123/api/services/light/turn_on -> Status 200
2026-01-02 14:30:15 | INFO     | core.domains.light  | ACAO [light] turn_on -> luz sala
2026-01-02 14:30:15 | INFO     | stt.server          | Resposta: luz sala ligada.
2026-01-02 14:30:15 | INFO     | stt.server          | ======================================================================
"""

# Exemplo 2: Comando com erro (timeout)
"""
2026-01-02 14:35:20 | INFO     | stt.server          | ======================================================================
2026-01-02 14:35:20 | INFO     | stt.server          | COMANDO: 'desligar ar do quarto'
2026-01-02 14:35:20 | INFO     | stt.server          | Intent parseada: off | Domain: climate
2026-01-02 14:35:20 | INFO     | core.dispatcher     | Despachando: climate.off
2026-01-02 14:35:20 | INFO     | core.domains.climate| Processando climate.off | Busca: 'ar quarto'
2026-01-02 14:35:20 | DEBUG    | core.domains.climate| Comodo identificado: 'ar quarto' -> quarto
2026-01-02 14:35:20 | DEBUG    | core.ha_client      | Chamando servico: script.desligar_ar_lg_quarto | Data: {}
2026-01-02 14:35:25 | ERROR    | core.ha_client      | API [POST] http://172.30.156.7:8123/api/services/script/desligar_ar_lg_quarto ** ERRO: Timeout (5s)
"""

# Exemplo 3: Comando com contexto (confirmação)
"""
2026-01-02 14:40:10 | INFO     | stt.server          | ======================================================================
2026-01-02 14:40:10 | INFO     | stt.server          | COMANDO: 'desligar luz'
2026-01-02 14:40:10 | INFO     | core.domains.light  | Multiplas luzes ligadas: 3 luz(es)
2026-01-02 14:40:10 | INFO     | stt.server          | Resposta: Mais de uma luz está ligada: sala, quarto, cozinha. Qual luz?
2026-01-02 14:40:10 | INFO     | stt.server          | ======================================================================

2026-01-02 14:40:15 | INFO     | stt.server          | ======================================================================
2026-01-02 14:40:15 | INFO     | stt.server          | COMANDO: 'sala'
2026-01-02 14:40:15 | INFO     | core.dispatcher     | Contexto ativo: light | Roteando confirmacao
2026-01-02 14:40:15 | INFO     | core.domains.light  | ACAO [light] turn_off -> light.sala
"""

# Exemplo 4: Comando não reconhecido
"""
2026-01-02 14:45:30 | INFO     | stt.server          | ======================================================================
2026-01-02 14:45:30 | INFO     | stt.server          | COMANDO: 'abrir janela'
2026-01-02 14:45:30 | INFO     | stt.server          | Intent parseada: None | Domain: None
2026-01-02 14:45:30 | WARNING  | core.dispatcher     | Dominio desconhecido: None
2026-01-02 14:45:30 | INFO     | stt.server          | Resposta: Não entendi. Pode repetir?
2026-01-02 14:45:30 | INFO     | stt.server          | ======================================================================
"""
