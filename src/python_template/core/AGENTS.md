# AGENTS.md — core/

Foundation layer: configuration (`config.py`) and logging (`logger.py`).
Everything in the package may import `core`; `core` imports nothing from the
rest of the package. Breaking that rule creates circular imports, because
`config`/`logger` are pulled in at module import time nearly everywhere.

## config.py — why it exists

Single source of truth for runtime configuration so that **no other module
ever touches `os.environ` or hardcodes a value**. Backed by pydantic-settings:
each field can be overridden by an environment variable of the same
(case-sensitive) name or a `.env` file. The module-level `settings = Settings()`
singleton is instantiated once at import — env vars must therefore be set
*before* the app imports anything, which is why tests that need different
settings should monkeypatch `settings` attributes rather than the environment.

Rules when adding a setting:
- Give it a safe default that works out of the box with zero setup — the
  template must run immediately after `uv sync` (that's why SQLite and
  `default-dev-key` are defaults; they are dev conveniences, not production
  recommendations).
- Mirror it in `.env.example` with a one-line comment.
- `SSE_MAX_EVENTS` exists so the SSE demo stream *terminates* — tests and some
  transports hang on infinite streams. Don't remove it.
- `API_KEY` / `API_KEY_NAME` drive the auth POC in `api/dependencies.py`; the
  CLI reads the same settings so client and server always agree on the key.

## logger.py — why it exists

One named logger (`python_template`) so log output is uniform and controllable
via `LOG_LEVEL` without every module configuring logging itself. `setup_logging()`
is called once per entry point (`api/main.py`, `cli/main.py`) — never call it
from library code, and never use `print()` or `logging.getLogger(__name__)`
elsewhere; import `logger` from here so all output shares one configuration.
