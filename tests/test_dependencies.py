from python_template.api.dependencies import (
    api_key_is_template_default,
    is_valid_api_key,
    ws_origin_allowed,
)
from python_template.core.config import settings


def test_is_valid_api_key_rejects_empty():
    assert is_valid_api_key(None) is False
    assert is_valid_api_key("") is False
    assert is_valid_api_key("wrong") is False
    assert is_valid_api_key(settings.API_KEY) is True


def test_ws_origin_allowed_wildcard():
    assert ws_origin_allowed(None) is True
    assert ws_origin_allowed("https://evil.example") is True


def test_ws_origin_allowed_allowlist(monkeypatch):
    monkeypatch.setattr(settings, "CORS_ORIGINS", ["http://localhost:8000"])
    assert ws_origin_allowed(None) is True
    assert ws_origin_allowed("http://localhost:8000") is True
    assert ws_origin_allowed("https://evil.example") is False


def test_api_key_is_template_default():
    assert api_key_is_template_default() is True
