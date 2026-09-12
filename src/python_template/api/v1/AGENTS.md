# AGENTS.md — api/v1/

Version-1 routers. Each file is one POC/feature area with its own
`router = APIRouter()`; `api/main.py` mounts them under `/api/v1` and applies
API-key protection on `items`, `sse`, and `ws`. Realtime demos take the same
key as HTTP (`X-API-KEY`, or `?api_key=` on WebSocket for browser clients).

## items.py — the canonical CRUD router

This file is the reference pattern every new resource router should copy:

- Routes are **thin**: validate via schema, call `crud/`, translate "not found"
  (`None`/`False` from CRUD) into `APIError(404)`. No queries or business
  logic in route functions — that belongs in `crud/` so the CLI or other
  entry points could reuse it.
- `response_model=` is set on **every** route. This is the serialization
  boundary that converts ORM objects to Pydantic and, critically, strips any
  fields not in the schema — without it, adding a sensitive column to the
  model would leak it in responses.
- List endpoints return `PaginatedResponse[...]` (`schemas/common.py`) —
  never a bare list. Bare lists can't carry `total`, which clients need for
  paging, and changing the shape later is a breaking API change.
- `skip`/`limit` use `Query(ge=..., le=...)` constraints: `limit >= 1` guards
  the `skip // limit` page math against ZeroDivisionError, `le=1000` caps
  response size.
- The `BackgroundTasks` usage is a deliberate demo of post-response work
  (fire-and-forget logging). Background tasks must not use the request's DB
  session — it's closed once the response is sent.

## sse.py — Server-Sent Events

The stream is intentionally **finite** (`SSE_MAX_EVENTS` from settings): tests
and some HTTP transports never terminate on `while True` streams. Do not
"fix" the loop to be infinite. The leading `":\n\n"` comment yield forces
headers to flush immediately so clients see the connection open; the
`asyncio.CancelledError` catch is the normal client-disconnect path, not an
error. SSE frames must keep the exact `event: ...\ndata: ...\n\n` wire format.

## ws.py — WebSocket

`ConnectionManager` holds connections in a plain in-process list — a POC
limitation, meaning broadcast only reaches clients on the *same worker
process*. That's fine for the demo; a real multi-worker deployment needs a
pub/sub backend (e.g. Redis), which is out of scope here. The
`WebSocketDisconnect` handler must always remove the socket from the manager.
`broadcast` iterates a copy and drops sockets whose `send_text` fails, so one
dead connection cannot abort the rest of the fan-out.

## Adding a new router

1. New file here with `router = APIRouter()`.
2. Schemas in `schemas/`, DB ops in `crud/`.
3. Register in `api/main.py` with prefix + tags, adding
   `dependencies=[Depends(get_api_key)]` if it must be protected.
4. Tests in `tests/` — remember the `X-API-KEY` header for protected routes.
