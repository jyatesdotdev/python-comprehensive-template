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
async def test_create_item():
    transport = ASGITransport(app=app)
    headers = {settings.API_KEY_NAME: settings.API_KEY}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        response = await ac.post(
            "/api/v1/items/", json={"name": "Test Item", "description": "Test Description"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data


@pytest.mark.asyncio
async def test_read_items():
    transport = ASGITransport(app=app)
    headers = {settings.API_KEY_NAME: settings.API_KEY}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        # Create an item first to have something to list
        await ac.post("/api/v1/items/", json={"name": "Item 1", "description": "Desc 1"})
        response = await ac.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_update_item():
    transport = ASGITransport(app=app)
    headers = {settings.API_KEY_NAME: settings.API_KEY}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        # Create
        res = await ac.post("/api/v1/items/", json={"name": "To Update", "description": "desc"})
        item_id = res.json()["id"]
        # Update
        response = await ac.put(f"/api/v1/items/{item_id}", json={"name": "Updated Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_item():
    transport = ASGITransport(app=app)
    headers = {settings.API_KEY_NAME: settings.API_KEY}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        # Create
        res = await ac.post("/api/v1/items/", json={"name": "To Delete", "description": "desc"})
        item_id = res.json()["id"]
        # Delete
        response = await ac.delete(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    assert response.json() is True


@pytest.mark.asyncio
async def test_item_not_found():
    transport = ASGITransport(app=app)
    headers = {settings.API_KEY_NAME: settings.API_KEY}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        response = await ac.get("/api/v1/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_unauthorized():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/items/")
    assert response.status_code == 403
