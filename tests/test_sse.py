import pytest
from python_template.core.config import settings


@pytest.mark.asyncio
async def test_sse(client):
    # Override settings for test speed
    original_max_events = settings.SSE_MAX_EVENTS
    settings.SSE_MAX_EVENTS = 2
    try:
        async with client.stream("GET", "/api/v1/sse") as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]
            
            lines = []
            async for line in response.aiter_lines():
                if line and not line.startswith(":"): # Skip empty lines and comments
                    lines.append(line)
                if len(lines) >= 2:
                    break
            
            assert any(line.startswith("event: ") for line in lines)
            assert any(line.startswith("data: ") for line in lines)
    finally:
        settings.SSE_MAX_EVENTS = original_max_events
