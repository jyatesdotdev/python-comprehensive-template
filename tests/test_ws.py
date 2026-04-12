from fastapi.testclient import TestClient

from python_template.api.main import app

client = TestClient(app)


def test_websocket():
    with client.websocket_connect("/api/v1/ws/123") as websocket:
        websocket.send_text("Hello WS")
        data = websocket.receive_text()
        assert data == "You wrote: Hello WS"
        data = websocket.receive_text()
        assert data == "Client #123 says: Hello WS"
