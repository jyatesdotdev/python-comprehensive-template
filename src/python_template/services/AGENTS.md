# AGENTS.md — services/

Clients and abstractions for things *outside* this application. The template
ships one: `rest_client.py`, a reusable async HTTP client wrapper that the CLI
uses to talk to our own API — demonstrating the client/server POC without
needing a second codebase.

## rest_client.py — design decisions to preserve

- **Why it exists at all** (instead of raw httpx calls): it centralizes the
  cross-cutting client concerns — retries, backoff, error normalization,
  timeouts — so callers write `await client.get("/path")` and get either
  parsed JSON or a single, typed `RESTClientError`. Callers must never need
  to import httpx.
- **Retry policy is deliberate:** 4xx responses are *not* retried (the
  request itself is wrong; retrying can't fix it and may duplicate writes) —
  except **429**, which is the server saying "try later". 5xx, network
  errors, and timeouts retry with exponential backoff
  (`retry_delay * 2**attempt`). If you touch `_request_with_retry`, keep this
  asymmetry; it is the core lesson of the file.
- `retry_delay` defaults small (0.1s) *because this is a template* — tests
  construct real clients and would crawl with production-scale backoff.
  Downstream projects tune it via the constructor.
- `RESTClientError` carries `status_code` and the parsed response `detail` so
  callers can render meaningful errors (the CLI prints them) without parsing
  httpx internals. Raise-from (`from e`) is kept so the underlying cause
  stays in tracebacks.
- The `transport` constructor parameter exists for **testing**: respx/ASGI
  transports plug in there. Don't remove it — it's what keeps the tests
  network-free.
- It's an async context manager; `async with RESTClient(...) as client:` is
  the required usage so connections are closed deterministically.

## Adding a new service

New external integration → new file/class here, same shape: config in
`core/config.py` (URLs, keys — never hardcoded), constructor accepting test
doubles, one service-specific error type, async throughout. Services may use
`crud/` and `core/`, but never import from `api/` or `cli/` — services are
callees of entry points, not callers.
