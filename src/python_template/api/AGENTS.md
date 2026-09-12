# AGENTS.md — api/

FastAPI application assembly. `main.py` is the composition root: it wires
middleware, exception handlers, and routers. Endpoint logic itself lives in
`v1/` (see `v1/AGENTS.md`) — keep `main.py` free of business logic so it stays
a readable map of the whole API surface.

## Why each file exists

- **`main.py`** — builds the `app` object. Auth is applied *here*, at
  `include_router(..., dependencies=[...])`, not inside each endpoint. HTTP
  routers use `get_api_key`; the WebSocket router uses `require_ws_api_key`
  (header or `api_key` query param, because browsers cannot set WS headers).
  `/` and `/health` stay public. If you add a router that must be protected,
  add the dependency in `main.py`; do not sprinkle auth checks inside route
  functions. Lifespan logs a warning if `API_KEY` is empty or still the
  template default.
- **`dependencies.py`** — the API-key auth POC. Single static key from
  settings. HTTP uses the `X-API-KEY` header (`secrets.compare_digest`,
  `auto_error=False` so a missing header is our 403). WebSocket auth is the
  same key via header or `?api_key=`; when `CORS_ORIGINS` is not `*`, browser
  Origins not on that list are rejected (CSWSH). A real deployment would swap
  these helpers for OAuth/JWT while keeping the same wiring in `main.py`.
- **`exceptions.py`** — defines `APIError` and the global handlers so every
  error response has the same envelope: `{"detail": ..., "status": "error"}`.
  The catch-all `Exception` handler exists to guarantee clients never see a
  raw stack trace and every unhandled error is logged with traceback.

## Rules

- Domain errors are raised as `APIError(message=..., status_code=...)`, not
  `HTTPException`. `HTTPException` appears only in `dependencies.py` (auth),
  because security dependencies run before our handler stack. Keeping one
  error type for domain failures is what keeps the response envelope uniform.
- The `lifespan` context manager is the sanctioned place for startup/shutdown
  work (the deprecated `@app.on_event` must not be reintroduced).
- `/health` intentionally returns 200 with `"status": "unhealthy"` rather than
  raising — orchestrators poll it and need a parseable body, not a 500.
- CORS origins default to `["*"]` because this is a dev template; the setting
  exists so downstream projects tighten it via config, not code.
  `allow_credentials` stays **False** while origins may be `*`: Starlette would
  otherwise reflect the request Origin. Turn credentials on only with an
  explicit origin allowlist.
- Routes are versioned under `/api/v1/...`. Breaking changes to a response
  shape mean a new `v2/` package, not edits to `v1` contracts.
