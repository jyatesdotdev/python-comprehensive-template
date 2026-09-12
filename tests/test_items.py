import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from python_template.api.main import app
from python_template.core.config import settings
from python_template.db.base import Base
from python_template.db.session import engine


@pytest_asyncio.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_item(auth_client):
    response = await auth_client.post(
        "/api/v1/items/",
        json={"name": "Test Item", "description": "Test Description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_item_rejects_empty_name(auth_client):
    response = await auth_client.post(
        "/api/v1/items/", json={"name": "", "description": "nope"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_items(auth_client):
    await auth_client.post(
        "/api/v1/items/", json={"name": "Item 1", "description": "Desc 1"}
    )
    response = await auth_client.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_read_items_pagination_metadata(auth_client):
    await auth_client.post("/api/v1/items/", json={"name": "Paged"})
    response = await auth_client.get("/api/v1/items/", params={"skip": 0, "limit": 10})
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["pages"] >= 1
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_read_items_rejects_limit_zero(auth_client):
    response = await auth_client.get("/api/v1/items/", params={"limit": 0})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_items_rejects_limit_too_large(auth_client):
    response = await auth_client.get("/api/v1/items/", params={"limit": 1001})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_read_items_rejects_negative_skip(auth_client):
    response = await auth_client.get("/api/v1/items/", params={"skip": -1})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_item(auth_client):
    res = await auth_client.post(
        "/api/v1/items/", json={"name": "To Update", "description": "keep me"}
    )
    item_id = res.json()["id"]
    response = await auth_client.put(
        f"/api/v1/items/{item_id}", json={"name": "Updated Name"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated Name"
    assert body["description"] == "keep me"


@pytest.mark.asyncio
async def test_update_item_rejects_null_name(auth_client):
    res = await auth_client.post(
        "/api/v1/items/", json={"name": "Keep", "description": "desc"}
    )
    item_id = res.json()["id"]
    response = await auth_client.put(f"/api/v1/items/{item_id}", json={"name": None})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_item(auth_client):
    res = await auth_client.post(
        "/api/v1/items/", json={"name": "To Delete", "description": "desc"}
    )
    item_id = res.json()["id"]
    response = await auth_client.delete(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    assert response.json() is True


@pytest.mark.asyncio
async def test_item_not_found(auth_client):
    response = await auth_client.get("/api/v1/items/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found", "status": "error"}


@pytest.mark.asyncio
async def test_update_item_not_found(auth_client):
    response = await auth_client.put("/api/v1/items/999", json={"name": "Nope"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found", "status": "error"}


@pytest.mark.asyncio
async def test_delete_item_not_found(auth_client):
    response = await auth_client.delete("/api/v1/items/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found", "status": "error"}


@pytest.mark.asyncio
async def test_unauthorized(client):
    response = await client.get("/api/v1/items/")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_wrong_api_key(client):
    response = await client.get(
        "/api/v1/items/", headers={settings.API_KEY_NAME: "wrong-key"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_empty_api_key_setting_rejects(client, monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "")
    response = await client.get("/api/v1/items/", headers={settings.API_KEY_NAME: ""})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_empty_configured_key_does_not_open_auth(client, monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "")
    transport = ASGITransport(app=app)
    headers = {settings.API_KEY_NAME: "not-empty"}
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=headers
    ) as ac:
        response = await ac.get("/api/v1/items/")
    assert response.status_code == 403
