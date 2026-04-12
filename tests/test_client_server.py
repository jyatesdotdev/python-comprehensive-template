import pytest
from httpx import ASGITransport

from python_template.api.main import app
from python_template.core.config import settings
from python_template.db.base import Base
from python_template.db.session import engine
from python_template.services.rest_client import RESTClient


@pytest.mark.asyncio
async def test_rest_client_with_api():
    # Setup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Setup transport for integration test
    transport = ASGITransport(app=app)
    headers = {settings.API_KEY_NAME: settings.API_KEY}

    # Use RESTClient with the real app's transport
    async with RESTClient(base_url="http://test", transport=transport, headers=headers) as client:
        # Test health check (no auth needed)
        health = await client.get("/health")
        assert health["status"] == "healthy"

        # Create an item (auth needed)
        new_item = await client.post("/api/v1/items/", data={"name": "Integration Item", "description": "From client"})
        assert new_item["name"] == "Integration Item"
        item_id = new_item["id"]

        # List items
        result = await client.get("/api/v1/items/")
        assert result["total"] >= 1
        assert any(item["id"] == item_id for item in result["items"])

        # Get one item
        item = await client.get(f"/api/v1/items/{item_id}")
        assert item["id"] == item_id

        # Update item
        updated = await client.put(f"/api/v1/items/{item_id}", data={"name": "Updated Integration"})
        assert updated["name"] == "Updated Integration"

        # Delete item
        deleted = await client.delete(f"/api/v1/items/{item_id}")
        assert deleted is True

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
