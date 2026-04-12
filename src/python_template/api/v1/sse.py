import asyncio
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from python_template.core.config import settings

router = APIRouter()


async def event_generator():
    # Using a limited range for this example to ensure compatibility with all transports/tests.
    # In a real application, this could be 'while True' for an infinite stream.
    for _ in range(settings.SSE_MAX_EVENTS):
        yield {
            "event": "message",
            "data": f"Current time is {datetime.now().strftime('%H:%M:%S')}",
        }
        await asyncio.sleep(0.1)


async def sse_wrapper():
    # Yield an initial comment to keep connection alive and ensure headers are sent
    yield ":\n\n"
    try:
        async for event in event_generator():
            yield f"event: {event['event']}\ndata: {event['data']}\n\n"
    except asyncio.CancelledError:
        # This is expected when the client disconnects
        pass


@router.get("/sse")
async def sse_endpoint():
    return StreamingResponse(
        sse_wrapper(),
        media_type="text/event-stream",
    )
