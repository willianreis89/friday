#!/bin/bash
# Script para executar testes com diferentes configuracoes

echo "============================================================"
echo "FRIDAY - SUITE DE TESTES"
echo "============================================================"

# Funcao para executar comando e verificar resultado
run_test() {
    echo ""
    echo ">> $1"
    eval $2
    if [ $? -eq 0 ]; then
        echo "   [OK] $1"
    else
        echo "   [FALHOU] $1"
        return 1
    fi
}

# Opcao 1: Todos os testes
if [ "$1" == "all" ] || [ -z "$1" ]; then
    echo ""
    echo "== Executando todos os testes =="
    pytest -v
fi

# Opcao 2: Testes com cobertura
if [ "$1" == "cov" ]; then
    echo ""
    echo "== Executando testes com cobertura =="
    pytest --cov=core --cov=stt --cov-report=term-missing --cov-report=html
    echo ""
    echo "Relatorio de cobertura gerado em: htmlcov/index.html"
fi

# Opcao 3: Testes rapidos (sem slow)
if [ "$1" == "fast" ]; then
    echo ""
    echo "== Executando testes rapidos =="
    pytest -v -m "not slow"
fi

# Opcao 4: Testes por modulo
if [ "$1" == "parser" ]; then
    run_test "Intent Parser" "pytest tests/test_intent_parser.py -v"
fi

if [ "$1" == "dispatcher" ]; then
    run_test "Dispatcher" "pytest tests/test_dispatcher.py -v"
fi

if [ "$1" == "light" ]; then
    run_test "Light Domain" "pytest tests/test_light.py -v"
fi

if [ "$1" == "climate" ]; then
    run_test "Climate Domain" "pytest tests/test_climate.py -v"
fi

if [ "$1" == "ha" ]; then
    run_test "Home Assistant Client" "pytest tests/test_ha_client.py -v"
fi

if [ "$1" == "context" ]; then
    run_test "Context Manager" "pytest tests/test_context_manager.py -v"
fi

# Opcao 5: CI mode (para integracao continua)
if [ "$1" == "ci" ]; then
    echo ""
    echo "== Modo CI - Testes completos com cobertura =="
    pytest --cov=core --cov=stt --cov-report=xml --cov-report=term -v
fi

# Help
if [ "$1" == "help" ] || [ "$1" == "-h" ]; then
    echo ""
    echo "Uso: ./run_tests.sh [opcao]"
    echo ""
    echo "Opcoes:"
    echo "  all       - Executa todos os testes (padrao)"
    echo "  cov       - Testes com relatorio de cobertura HTML"
    echo "  fast      - Apenas testes rapidos"
    echo "  parser    - Apenas testes do intent_parser"
    echo "  dispatcher- Apenas testes do dispatcher"
    echo "  light     - Apenas testes do dominio light"
    echo "  climate   - Apenas testes do dominio climate"
    echo "  ha        - Apenas testes do ha_client"
    echo "  context   - Apenas testes do context_manager"
    echo "  ci        - Modo CI com cobertura XML"
    echo "  help      - Mostra esta mensagem"
    echo ""
fi

echo ""
echo "============================================================"
