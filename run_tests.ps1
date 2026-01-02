# Script PowerShell para executar testes no Windows

param(
    [string]$Option = "all"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "FRIDAY - SUITE DE TESTES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

function Run-Test {
    param([string]$Name, [string]$Command)
    Write-Host ""
    Write-Host ">> $Name" -ForegroundColor Yellow
    Invoke-Expression $Command
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] $Name" -ForegroundColor Green
    } else {
        Write-Host "   [FALHOU] $Name" -ForegroundColor Red
    }
}

switch ($Option) {
    "all" {
        Write-Host ""
        Write-Host "== Executando todos os testes ==" -ForegroundColor Yellow
        pytest -v
    }
    
    "cov" {
        Write-Host ""
        Write-Host "== Executando testes com cobertura ==" -ForegroundColor Yellow
        pytest --cov=core --cov=stt --cov-report=term-missing --cov-report=html
        Write-Host ""
        Write-Host "Relatorio de cobertura gerado em: htmlcov\index.html" -ForegroundColor Green
    }
    
    "fast" {
        Write-Host ""
        Write-Host "== Executando testes rapidos ==" -ForegroundColor Yellow
        pytest -v -m "not slow"
    }
    
    "parser" {
        Run-Test "Intent Parser" "pytest tests/test_intent_parser.py -v"
    }
    
    "dispatcher" {
        Run-Test "Dispatcher" "pytest tests/test_dispatcher.py -v"
    }
    
    "light" {
        Run-Test "Light Domain" "pytest tests/test_light.py -v"
    }
    
    "climate" {
        Run-Test "Climate Domain" "pytest tests/test_climate.py -v"
    }
    
    "ha" {
        Run-Test "Home Assistant Client" "pytest tests/test_ha_client.py -v"
    }
    
    "context" {
        Run-Test "Context Manager" "pytest tests/test_context_manager.py -v"
    }
    
    "ci" {
        Write-Host ""
        Write-Host "== Modo CI - Testes completos com cobertura ==" -ForegroundColor Yellow
        pytest --cov=core --cov=stt --cov-report=xml --cov-report=term -v
    }
    
    "help" {
        Write-Host ""
        Write-Host "Uso: .\run_tests.ps1 [opcao]" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Opcoes:" -ForegroundColor Yellow
        Write-Host "  all        - Executa todos os testes (padrao)"
        Write-Host "  cov        - Testes com relatorio de cobertura HTML"
        Write-Host "  fast       - Apenas testes rapidos"
        Write-Host "  parser     - Apenas testes do intent_parser"
        Write-Host "  dispatcher - Apenas testes do dispatcher"
        Write-Host "  light      - Apenas testes do dominio light"
        Write-Host "  climate    - Apenas testes do dominio climate"
        Write-Host "  ha         - Apenas testes do ha_client"
        Write-Host "  context    - Apenas testes do context_manager"
        Write-Host "  ci         - Modo CI com cobertura XML"
        Write-Host "  help       - Mostra esta mensagem"
        Write-Host ""
    }
    
    default {
        Write-Host ""
        Write-Host "Opcao invalida. Use 'help' para ver opcoes disponiveis." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
