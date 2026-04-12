import pytest
import respx
from httpx import Response

from python_template.services.rest_client import RESTClient


@pytest.mark.asyncio
@respx.mock
async def test_rest_client_get():
    respx.get("https://api.example.com/items").mock(return_value=Response(200, json=[{"id": 1, "name": "Test"}]))
    
    async with RESTClient(base_url="https://api.example.com") as client:
        result = await client.get("/items")
        assert len(result) == 1
        assert result[0]["name"] == "Test"


@pytest.mark.asyncio
@respx.mock
async def test_rest_client_post():
    respx.post("https://api.example.com/items").mock(return_value=Response(201, json={"id": 1, "name": "New Item"}))
    
    async with RESTClient(base_url="https://api.example.com") as client:
        result = await client.post("/items", data={"name": "New Item"})
        assert result["id"] == 1
        assert result["name"] == "New Item"
