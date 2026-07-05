# AGENTS.md — tests/

Pytest suite. Configuration lives in `pyproject.toml` (`[tool.pytest.ini_options]`),
and two settings there shape how you write tests:

- `asyncio_mode = "auto"` — `async def` tests just work; you'll see
  `@pytest.mark.asyncio` on older tests but it is not required for new ones.
- `addopts` enforces **coverage ≥ 80% of `src/python_template`**. This means
  an untested new module can make the whole suite fail even though every test
  passes — if `make test` fails with a coverage message, add tests, don't
  lower the threshold.

Run with `make test` (or `uv run pytest tests/test_x.py -k name` for one test).

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
- **Auth:** protected endpoints need
  `headers={settings.API_KEY_NAME: settings.API_KEY}` — read both from
  `settings`, never hardcode `"X-API-KEY"`/`"default-dev-key"`, so a config
  change can't silently break the suite. `test_unauthorized` exists to pin
  the 403 behavior; keep an equivalent when adding protected routers.
- **CLI:** use `typer.testing.CliRunner().invoke(app, [...])` and assert on
  `result.stdout` / `result.stderr` / `exit_code`. Mock the boundary
  (`respx` for HTTP, `unittest.mock.patch` for uvicorn/alembic) — CLI tests
  verify wiring and output, not the server underneath.
- The shared `client` fixture in `conftest.py` is intentionally
  **unauthenticated**; build your own client with headers for protected
  routes (as `test_items.py` does).

## Lint notes

`tests/*` has ruff per-file-ignores for `PLR2004` (magic values) and `S101`
(assert) — literal numbers and bare asserts are fine in tests. Everything
else (import order, naming, pyupgrade) still applies.
