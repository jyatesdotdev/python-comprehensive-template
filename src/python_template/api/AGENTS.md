# AGENTS.md — api/

FastAPI application assembly. `main.py` is the composition root: it wires
middleware, exception handlers, and routers. Endpoint logic itself lives in
`v1/` (see `v1/AGENTS.md`) — keep `main.py` free of business logic so it stays
a readable map of the whole API surface.

## Why each file exists

- **`main.py`** — builds the `app` object. Auth is applied *here*, at
  `include_router(..., dependencies=[Depends(get_api_key)])`, not inside each
  endpoint. That is a deliberate choice: protection is decided once per router
  at registration, so it's impossible to forget on an individual endpoint. If
  you add a router that must be protected, add the dependency in `main.py`; do
  not sprinkle auth checks inside route functions.
- **`dependencies.py`** — the API-key auth POC. Single static key from
  settings, sent in the `X-API-KEY` header. Uses `secrets.compare_digest`
  (timing-safe comparison) and `auto_error=False` so a *missing* header falls
  through to our own 403 rather than FastAPI's default error shape. This is a
  demo of the dependency-injection auth pattern — a real deployment would swap
  the body of `get_api_key` for OAuth/JWT while keeping the same wiring.
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
- CORS is wide open (`["*"]`) because this is a dev template; the setting
  exists precisely so downstream projects tighten it via config, not code.
- Routes are versioned under `/api/v1/...`. Breaking changes to a response
  shape mean a new `v2/` package, not edits to `v1` contracts.
