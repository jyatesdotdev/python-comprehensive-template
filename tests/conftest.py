import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from python_template.api.main import app
from python_template.core.config import settings


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client():
    transport = ASGITransport(app=app)
    headers = {settings.API_KEY_NAME: settings.API_KEY}
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=headers
    ) as ac:
        yield ac
