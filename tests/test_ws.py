from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from python_template.api.main import app
from python_template.api.v1.ws import ConnectionManager
from python_template.core.config import settings

client = TestClient(app)


def _ws_headers() -> dict[str, str]:
    return {settings.API_KEY_NAME: settings.API_KEY}


def test_websocket():
    with client.websocket_connect("/api/v1/ws/123", headers=_ws_headers()) as websocket:
        websocket.send_text("Hello WS")
        data = websocket.receive_text()
        assert data == "You wrote: Hello WS"
        data = websocket.receive_text()
        assert data == "Client #123 says: Hello WS"


def test_websocket_query_param_auth():
    with client.websocket_connect(
        f"/api/v1/ws/123?api_key={settings.API_KEY}"
    ) as websocket:
        websocket.send_text("Hello WS")
        assert websocket.receive_text() == "You wrote: Hello WS"


def test_websocket_unauthorized():
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/api/v1/ws/123") as websocket:
            websocket.send_text("nope")


def test_websocket_origin_rejected_when_cors_allowlist(monkeypatch):
    monkeypatch.setattr(settings, "CORS_ORIGINS", ["http://localhost:8000"])
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            "/api/v1/ws/123",
            headers={**_ws_headers(), "Origin": "https://evil.example"},
        ) as websocket:
            websocket.send_text("nope")


@pytest.mark.asyncio
async def test_broadcast_drops_dead_sockets():
    manager = ConnectionManager()
    dead = AsyncMock()
    dead.send_text.side_effect = Exception("gone")
    live = AsyncMock()
    manager.active_connections = [dead, live]
    await manager.broadcast("hi")
    live.send_text.assert_awaited_once_with("hi")
    assert dead not in manager.active_connections
    assert live in manager.active_connections


def test_disconnect_missing_socket_is_safe():
    manager = ConnectionManager()
    manager.disconnect(AsyncMock())
