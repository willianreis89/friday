# Friday - Assistente Virtual para Home Assistant

Assistente virtual em Python integrado ao Home Assistant para controlar dispositivos de automação residencial via comandos de voz.

## 🚀 Setup Rápido

### 1. Clonar o repositório
```bash
git clone https://github.com/willianreis89/friday.git
cd friday
```

### 2. Criar ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais do Home Assistant
```

**Variáveis obrigatórias:**
- `HA_URL`: URL do seu Home Assistant (ex: `http://192.168.1.100:8123`)
- `HA_TOKEN`: Token de acesso de longa duração (criar em: Perfil → Tokens de acesso de longa duração)

### 5. Executar o servidor
```bash
uvicorn stt.server:app --reload --host 0.0.0.0 --port 8000
```

## 📡 Uso da API

### Enviar comando
```bash
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"text": "ligar luz da sala"}'
```

### Resposta
```json
{
  "intent": "on",
  "domain": "light",
  "response": {"message": "sala ligada."}
}
```

## 🎯 Comandos Suportados

### Luzes
- `ligar luz da sala`
- `apagar todas as luzes`
- `ligar luz do quarto e desligar luz da cozinha`

### Ar-condicionado
- `ligar ar do quarto`
- `desligar ar` (desliga o único ligado ou pergunta qual)
- `desligar todos os ares`

## 🏗️ Arquitetura

```
friday/
├── core/
│   ├── intent_parser.py     # Extrai intenção do texto
│   ├── dispatcher.py         # Roteia para domínios
│   ├── context_manager.py    # Gerencia confirmações
│   ├── ha_client.py          # Cliente Home Assistant API
│   └── domains/              # Handlers por domínio
│       ├── light.py
│       ├── climate.py
│       └── ...
├── stt/
│   └── server.py             # API FastAPI
├── utils/
│   └── logger.py             # Sistema de logging
└── logs/                     # Logs de execução
```

## 📋 Logs e Monitoramento

O sistema gera logs estruturados em dois destinos:

**Console (INFO+):**
- Comandos recebidos
- Ações executadas
- Respostas enviadas

**Arquivo (DEBUG+):** `logs/friday.log`
- Normalizações de texto
- Buscas de entidades
- Chamadas à API do Home Assistant
- Erros e timeouts detalhados

**Rotação automática de logs:**
- **Estratégia padrão:** Rotação diária à meia-noite
- **Retenção:** 30 dias de histórico
- **Arquivos rotacionados:** `friday.log.2026-01-01`, `friday.log.2026-01-02`, etc.
- **Alternativa:** Rotação por tamanho (10MB, 7 arquivos)

Para alterar a estratégia, edite [utils/logger.py](utils/logger.py):
```python
USE_TIME_ROTATION = True   # Diária (padrão)
# ou
USE_TIME_ROTATION = False  # Por tamanho
```

**Exemplo de log:**
```
2026-01-02 14:30:15 | INFO     | stt.server          | COMANDO: 'ligar luz da sala'
2026-01-02 14:30:15 | INFO     | core.intent_parser  | Intent parseada: on | Domain: light
2026-01-02 14:30:15 | INFO     | core.dispatcher     | Despachando: light.on
2026-01-02 14:30:15 | INFO     | core.domains.light  | Processando light.on
2026-01-02 14:30:15 | INFO     | core.ha_client      | API [POST] http://ha:8123/api/services/light/turn_on -> Status 200
2026-01-02 14:30:15 | INFO     | core.domains.light  | ACAO [light] turn_on -> sala
```

**Níveis de log disponíveis:**
- `DEBUG`: Informações técnicas detalhadas
- `INFO`: Operações normais
- `WARNING`: Situações inesperadas mas tratáveis
- `ERROR`: Erros que impedem operações

**Limpeza manual de logs antigos:**
```bash
# Linux/Mac
find logs/ -name "friday.log.*" -mtime +30 -delete

# Windows
Get-ChildItem logs\friday.log.* | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

Para mais detalhes sobre rotação, veja [logs/ROTACAO.txt](logs/ROTACAO.txt)

## 🔐 Segurança

⚠️ **NUNCA** commite o arquivo `.env` com credenciais reais!

O `.gitignore` já está configurado para ignorar:
- `.env`
- `.env.*`
- Tokens e credenciais

## � Testes

O projeto possui uma suíte completa de testes unitários com >100 testes.

### Executar testes

**Todos os testes:**
```bash
pytest
```

**Com cobertura:**
```bash
pytest --cov=core --cov=stt --cov-report=html
# Abra htmlcov/index.html no navegador
```

**Teste específico:**
```bash
pytest tests/test_intent_parser.py
```

**Scripts auxiliares:**
```bash
# Linux/Mac
./run_tests.sh cov

# Windows
.\run_tests.ps1 cov
```

### Estrutura de testes

```
tests/
├── test_intent_parser.py    # Parsing de comandos (40+ testes)
├── test_dispatcher.py        # Roteamento (10+ testes)
├── test_context_manager.py   # Contexto (10+ testes)
├── test_ha_client.py         # API Home Assistant (15+ testes)
├── test_light.py             # Domínio de luz (15+ testes)
└── test_climate.py           # Domínio de clima (15+ testes)
```

Meta de cobertura: **> 80%**

## �🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Adiciona nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📝 Licença

Este projeto é de código aberto.
