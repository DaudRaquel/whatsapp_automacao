"""Testes de configuração e utilitários do WhatsApp bot."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest


def test_type_humanlike_delay():
    """Verifica que a digitação humanizada adiciona delay entre caracteres."""
    import time
    from unittest.mock import MagicMock, patch

    element = MagicMock()
    start = time.time()

    with patch("time.sleep") as mock_sleep:
        from bot import WhatsAppBot
        bot = WhatsAppBot("true", False, lambda t,c: None, lambda p: None)
        bot._type_humanlike(element, "abc")
        assert mock_sleep.call_count == 3   # 3 caracteres = 3 sleeps


def test_callbacks_sao_chamados():
    """on_status e on_progress devem ser chamáveis."""
    status_calls, progress_calls = [], []

    from bot import WhatsAppBot
    bot = WhatsAppBot(
        acao="true",
        reutilizar_sessao=False,
        on_status=lambda t, c: status_calls.append((t, c)),
        on_progress=lambda p: progress_calls.append(p),
    )
    bot.on_status("Teste", "verde")
    bot.on_progress(0.5)
    assert status_calls == [("Teste", "verde")]
    assert progress_calls == [0.5]


def test_max_erros_config(monkeypatch):
    monkeypatch.setenv("MAX_CONSECUTIVE_ERRORS", "5")
    import importlib, config
    importlib.reload(config)
    assert config.MAX_CONSECUTIVE_ERRORS == 5
