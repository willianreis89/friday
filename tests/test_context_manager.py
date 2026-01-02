"""
Testes para core.context_manager

Testa o gerenciamento de contexto para confirmacoes
"""
import time

import pytest

from core.context_manager import ContextManager


class TestContextManager:
    """Testes para a classe ContextManager"""
    
    def test_init_empty(self):
        """Contexto deve iniciar vazio"""
        ctx = ContextManager()
        assert ctx.data is None
        assert not ctx.valid()
    
    def test_set_context(self):
        """Deve definir contexto com payload"""
        ctx = ContextManager()
        payload = {"domain": "light", "action": "off"}
        ctx.set(payload)
        
        assert ctx.data is not None
        assert ctx.data["payload"] == payload
        assert "expires" in ctx.data
        assert ctx.valid()
    
    def test_set_context_with_custom_ttl(self):
        """Deve aceitar TTL customizado"""
        ctx = ContextManager()
        payload = {"domain": "climate"}
        ctx.set(payload, ttl=5)
        
        assert ctx.valid()
        assert ctx.data is not None
        # Verifica que expira em aproximadamente 5 segundos
        assert ctx.data["expires"] > time.time()  # type: ignore
        assert ctx.data["expires"] <= time.time() + 6  # type: ignore
    
    def test_clear_context(self):
        """Deve limpar contexto"""
        ctx = ContextManager()
        ctx.set({"domain": "light"})
        
        assert ctx.valid()
        
        ctx.clear()
        assert ctx.data is None
        assert not ctx.valid()
    
    def test_valid_returns_false_when_empty(self):
        """valid() deve retornar False quando vazio"""
        ctx = ContextManager()
        assert not ctx.valid()
    
    def test_valid_returns_true_when_active(self):
        """valid() deve retornar True quando ativo"""
        ctx = ContextManager()
        ctx.set({"domain": "light"}, ttl=10)
        assert ctx.valid()
    
    def test_valid_returns_false_after_expiration(self):
        """valid() deve retornar False apos expiracao"""
        ctx = ContextManager()
        ctx.set({"domain": "light"}, ttl=1)  # 1 segundo
        
        assert ctx.valid()
        
        time.sleep(1.2)  # Espera expirar
        assert not ctx.valid()
    
    def test_context_payload_accessible(self):
        """Payload deve ser acessivel via data"""
        ctx = ContextManager()
        payload = {
            "domain": "climate",
            "action": "off",
            "candidates": [{"room": "quarto"}]
        }
        ctx.set(payload)
        
        assert ctx.data is not None
        assert ctx.data["payload"]["domain"] == "climate"
        assert ctx.data["payload"]["action"] == "off"
        assert len(ctx.data["payload"]["candidates"]) == 1
    
    def test_multiple_set_overwrites(self):
        """set() multiplos devem sobrescrever"""
        ctx = ContextManager()
        ctx.set({"domain": "light"})
        
        assert ctx.data is not None
        assert ctx.data["payload"]["domain"] == "light"
        
        ctx.set({"domain": "climate"})
        assert ctx.data is not None
        assert ctx.data["payload"]["domain"] == "climate"
    
    def test_ttl_default_value(self):
        """TTL default deve ser 10 segundos"""
        ctx = ContextManager()
        start = time.time()
        ctx.set({"test": "data"})
        
        assert ctx.data is not None
        expected_expiry = start + 10
        # Tolerancia de 1 segundo
        assert abs(ctx.data["expires"] - expected_expiry) < 1  # type: ignore
