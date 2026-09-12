# AGENTS.md — tests/

Pytest suite. Configuration lives in `pyproject.toml` (`[tool.pytest.ini_options]`),
and two settings there shape how you write tests:

- `asyncio_mode = "auto"` — `async def` tests just work; you'll see
  `@pytest.mark.asyncio` on older tests but it is not required for new ones.
- `addopts` enforces **coverage ≥ 80% of `python_template`**. `[tool.coverage.run]`
  sets `concurrency = ["greenlet", "thread"]` so SQLAlchemy asyncio work is
  counted — do not remove it or CRUD/router bodies look uncovered. An untested
  new module can make the whole suite fail even though every test passes — if
  `make test` fails with a coverage message, add tests, don't lower the threshold.

Run with `make test` (or `uv run pytest tests/test_x.py -k name --no-cov` for
one test). `addopts` always applies `--cov-fail-under=80` against the whole
package, so a targeted run without `--no-cov` fails even when the test passes.

## How things are tested here (match the existing style)

- **No network, no live server, ever.** API tests use
  `httpx.AsyncClient(transport=ASGITransport(app=app))` to call the FastAPI
  app in-process; external HTTP is mocked with `respx`; the integration test
  (`test_client_server.py`) plugs the ASGI transport into `RESTClient` — that
  is the whole reason `RESTClient` has a `transport` parameter. Tests must
  stay runnable offline and in CI without services.
- **Database:** tests hit the real (SQLite `test.db`) engine. Files that need
  tables use a `create_all`/`drop_all` fixture (see `test_items.py`'s autouse
  `init_db`). Alembic is *not* used in tests — migrations are exercised only
  via mocks in `test_cli.py`. Because the DB file is shared across the
  session, don't assert exact row counts (`total >= 1`, not `total == 1`);
  other tests may have written rows.
- **Auth:** use the `auth_client` fixture in `conftest.py` for protected
  routes. It reads `{settings.API_KEY_NAME: settings.API_KEY}` — never hardcode
  `"X-API-KEY"`/`"default-dev-key"`. The shared `client` fixture stays
  unauthenticated. Pin missing-header **and** wrong-key 403s (`test_unauthorized`,
  `test_wrong_api_key`); keep equivalents when adding protected routers.
- **WebSocket:** Starlette `TestClient.websocket_connect` is the remaining
  sync client — httpx has no WS transport here. Pass `headers=` with the API
  key (or `?api_key=`). Unauthorized connects must raise `WebSocketDisconnect`.
- **CLI:** use `typer.testing.CliRunner().invoke(app, [...])` and assert on
  `result.stdout` / `result.stderr` / `result.exit_code`. Failed commands must
  exit `1`. Mock the boundary (`respx` for HTTP, `unittest.mock.patch` for
  uvicorn/alembic) — CLI tests verify wiring and output, not the server
  underneath.

## Lint notes

`tests/*` has a ruff per-file-ignore for `PLR2004` (magic values) — literal
numbers are fine in tests. Everything else (import order, naming, pyupgrade)
still applies. There is no ruff `S` (bandit-in-ruff) select; security lint is
Bandit via `make security` / `security.yml`.
