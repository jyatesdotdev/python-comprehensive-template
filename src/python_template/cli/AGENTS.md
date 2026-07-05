# AGENTS.md — cli/

Typer CLI — the second entry point over the same core as the API. Its purpose
in the template is to demonstrate that a CLI can be an *API client* rather
than a second implementation: the `items` commands call the HTTP API through
`services.rest_client.RESTClient` instead of touching `crud/` directly. Keep
that pattern — it exercises the client/server POC and guarantees CLI and API
behavior can't drift apart.

## Rules and established patterns

- **Async bridge:** Typer commands are sync. Wrap async work in an inner
  `async def _impl()` and call `asyncio.run(_impl())` — the pattern used by
  `check_health` and the `items` commands. Never make the command function
  itself `async` (Typer won't await it; the command silently does nothing).
- **Output vs. logging:** `typer.echo()` is the user-facing output;
  `logger` is diagnostics. Don't log what the user needs to read, don't
  `echo` what only an operator needs. Errors go to `typer.echo(..., err=True)`
  so stdout stays parseable.
- **Auth:** commands that hit protected endpoints send
  `{settings.API_KEY_NAME: settings.API_KEY}` as headers — client and server
  read the *same* settings object, which is why they always agree on the key.
- **Sub-apps:** related commands are grouped with `typer.Typer()` +
  `app.add_typer(sub, name="...")` (`items`, `db`). Add new command groups the
  same way rather than flat top-level commands.
- The `serve` command's `0.0.0.0` default carries `# nosec B104`: bandit flags
  binding all interfaces, but for a dev-server launcher it's intentional. Keep
  the suppression (bandit needs `nosec`, not ruff's `noqa`) if you touch that
  line.
- **`db init`** imports Alembic *inside* the function (with `noqa: PLC0415`)
  deliberately — it keeps Alembic out of the import path of every other
  command, so `--help` and simple commands stay fast and don't require
  migration config to be importable.
- Commands must not crash with tracebacks on expected failures (server down,
  bad key): catch, log, echo an error — the CLI is a demo of good UX too.
- Failure exit codes are currently 0 even on error; if you improve this, use
  `raise typer.Exit(code=1)`, and update `tests/test_cli.py` expectations.
