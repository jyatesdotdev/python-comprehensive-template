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
- **`serve` defaults to `127.0.0.1` with `reload=False`.** Binding all interfaces
  is a Docker/compose concern (`0.0.0.0` in the image CMD), not the CLI default.
  Use `--host 0.0.0.0` / `--reload` explicitly when you mean it. If you put a
  literal `0.0.0.0` default back, bandit will flag it (`B104`) and needs
  `# nosec B104` on that line — ruff `# noqa` does nothing for bandit.
- **`db init`** imports Alembic *inside* the function (with `noqa: PLC0415`)
  deliberately — it keeps Alembic out of the import path of every other
  command, so `--help` and simple commands stay fast and don't require
  migration config to be importable.
- Commands must not crash with tracebacks on expected failures (server down,
  bad key): catch, log, echo an error — the CLI is a demo of good UX too.
- Failed commands `raise typer.Exit(code=1)` after echoing the error. Keep
  `tests/test_cli.py` pinned to non-zero exit codes on those paths.
