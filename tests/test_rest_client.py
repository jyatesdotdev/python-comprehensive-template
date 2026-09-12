from unittest.mock import AsyncMock

import pytest
import respx
from httpx import Response

from python_template.services.rest_client import RESTClient, RESTClientError


@pytest.mark.asyncio
@respx.mock
async def test_rest_client_get():
    respx.get("https://api.example.com/items").mock(
        return_value=Response(200, json=[{"id": 1, "name": "Test"}])
    )

    async with RESTClient(base_url="https://api.example.com") as client:
        result = await client.get("/items")
        assert len(result) == 1
        assert result[0]["name"] == "Test"


@pytest.mark.asyncio
@respx.mock
async def test_rest_client_post():
    respx.post("https://api.example.com/items").mock(
        return_value=Response(201, json={"id": 1, "name": "New Item"})
    )

    async with RESTClient(base_url="https://api.example.com") as client:
        result = await client.post("/items", data={"name": "New Item"})
        assert result["id"] == 1
        assert result["name"] == "New Item"


@pytest.mark.asyncio
@respx.mock
async def test_rest_client_400_does_not_retry():
    route = respx.get("https://api.example.com/items").mock(
        return_value=Response(400, json={"detail": "bad"})
    )

    async with RESTClient(base_url="https://api.example.com") as client:
        with pytest.raises(RESTClientError) as exc:
            await client.get("/items")

    assert exc.value.status_code == 400
    assert route.call_count == 1


@pytest.mark.asyncio
@respx.mock
async def test_rest_client_500_retries(monkeypatch):
    monkeypatch.setattr(
        "python_template.services.rest_client.asyncio.sleep", AsyncMock()
    )
    route = respx.get("https://api.example.com/items").mock(
        return_value=Response(500, json={"detail": "oops"})
    )

    async with RESTClient(
        base_url="https://api.example.com", max_retries=2, retry_delay=0
    ) as client:
        with pytest.raises(RESTClientError):
            await client.get("/items")

    assert route.call_count == 3


@pytest.mark.asyncio
@respx.mock
async def test_rest_client_429_retries(monkeypatch):
    monkeypatch.setattr(
        "python_template.services.rest_client.asyncio.sleep", AsyncMock()
    )
    route = respx.get("https://api.example.com/items").mock(
        return_value=Response(429, json={"detail": "slow down"})
    )

    async with RESTClient(
        base_url="https://api.example.com", max_retries=1, retry_delay=0
    ) as client:
        with pytest.raises(RESTClientError):
            await client.get("/items")

    assert route.call_count == 2


@pytest.mark.asyncio
@respx.mock
async def test_rest_client_non_json_2xx():
    respx.get("https://api.example.com/items").mock(
        return_value=Response(200, text="not-json")
    )

    async with RESTClient(base_url="https://api.example.com") as client:
        with pytest.raises(RESTClientError) as exc:
            await client.get("/items")

    assert "not JSON" in exc.value.message
    assert exc.value.status_code == 200
