from unittest.mock import MagicMock, patch

import pytest

from python_template.api.main import app, lifespan
from python_template.core.config import settings


@pytest.mark.asyncio
async def test_read_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Python Template API"}


@pytest.mark.asyncio
async def test_read_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}


@pytest.mark.asyncio
async def test_read_health_unhealthy(client):
    mock_engine = MagicMock()
    mock_engine.connect.side_effect = Exception("db down")
    with patch("python_template.api.main.engine", mock_engine):
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "unhealthy", "database": "disconnected"}


@pytest.mark.asyncio
async def test_lifespan_warns_on_default_key(caplog):
    with caplog.at_level("WARNING"):
        async with lifespan(app):
            pass
    assert "template default" in caplog.text


@pytest.mark.asyncio
async def test_lifespan_warns_on_empty_key(caplog, monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "")
    with caplog.at_level("WARNING"):
        async with lifespan(app):
            pass
    assert "empty" in caplog.text


@pytest.mark.asyncio
async def test_cors_wildcard_does_not_allow_credentials(client):
    response = await client.get("/", headers={"Origin": "https://evil.example"})
    assert response.headers.get("access-control-allow-origin") == "*"
    assert response.headers.get("access-control-allow-credentials") != "true"
