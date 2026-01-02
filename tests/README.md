==============================================================
TESTES UNITARIOS - FRIDAY
==============================================================

Este diretorio contem todos os testes unitarios do projeto.

==============================================================
## ESTRUTURA DE TESTES
==============================================================

tests/
  __init__.py                  # Package tests
  test_intent_parser.py        # Parsing de comandos (40+ testes)
  test_context_manager.py      # Gerenciamento de contexto (10+ testes)
  test_ha_client.py            # Cliente Home Assistant (15+ testes)
  test_dispatcher.py           # Roteamento de comandos (10+ testes)
  test_light.py                # Handlers de luz (15+ testes)
  test_climate.py              # Handlers de ar-condicionado (15+ testes)

==============================================================
## EXECUTAR TESTES
==============================================================

** Executar todos os testes:
pytest

** Executar com cobertura:
pytest --cov=core --cov=stt --cov-report=html

** Executar teste especifico:
pytest tests/test_intent_parser.py

** Executar classe especifica:
pytest tests/test_intent_parser.py::TestNormalize

** Executar teste especifico:
pytest tests/test_intent_parser.py::TestNormalize::test_normalize_remove_acentos

** Modo verboso:
pytest -v

** Mostrar print statements:
pytest -s

** Parar no primeiro erro:
pytest -x

** Executar apenas testes lentos:
pytest -m slow

** Executar exceto testes lentos:
pytest -m "not slow"

==============================================================
## COBERTURA DE CODIGO
==============================================================

Apos executar testes com cobertura, um relatorio HTML sera gerado em:
  htmlcov/index.html

Abra no navegador para ver cobertura detalhada linha por linha.

Meta de cobertura: > 80%

==============================================================
## ESTRUTURA DE TESTES
==============================================================

Cada arquivo de teste contem:

1. Classes organizadas por funcionalidade
2. Metodos setup_method() para preparar ambiente
3. Uso extensivo de mocks para isolar dependencias
4. Assertions claras e especificas
5. Docstrings explicando o que cada teste verifica

Exemplo:
```python
class TestNormalize:
    def test_normalize_remove_acentos(self):
        '''Deve remover acentos e caracteres especiais'''
        assert normalize("ligar lampada") == "ligar lampada"
```

==============================================================
## MOCKS E FIXTURES
==============================================================

** patch: Mock de funcoes e modulos
```python
@patch('core.ha_client.requests.post')
def test_call_service(mock_post):
    mock_post.return_value.status_code = 200
```

** Mock de retorno:
```python
mock_function.return_value = {"result": "success"}
```

** Mock de excecao:
```python
mock_function.side_effect = Exception("Error")
```

** Mock de multiplas chamadas:
```python
mock_function.side_effect = [True, False, True]
```

==============================================================
## BOAS PRATICAS
==============================================================

1. Um teste deve testar apenas uma coisa
2. Testes devem ser independentes (nao depender de ordem)
3. Use mocks para dependencias externas (API, banco, etc)
4. Limpe estado compartilhado (context.clear())
5. Nomes descritivos: test_should_do_something_when_condition
6. Assertions especificas e claras
7. Use fixtures para setup complexo

==============================================================
## INTEGRACAO CONTINUA
==============================================================

Para CI/CD, adicione ao workflow:

```yaml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=core --cov=stt --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

==============================================================
## ADICIONAR NOVOS TESTES
==============================================================

1. Criar arquivo test_<modulo>.py
2. Importar o que sera testado
3. Criar classes agrupando testes relacionados
4. Implementar testes com mocks necessarios
5. Executar e verificar se passam
6. Verificar cobertura

==============================================================
## DEBUGGING TESTES
==============================================================

** Ver output completo de erro:
pytest --tb=long

** Modo interativo (pdb):
pytest --pdb

** Ultimo teste que falhou:
pytest --lf

** Executar testes modificados:
pytest --testmon

==============================================================
FIM
==============================================================
