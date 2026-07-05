# AGENTS.md — python_template package

Top-level package for the template. It deliberately exposes **two entry
points over one shared core**: an HTTP API (`api/`) and a CLI (`cli/`). The
point being demonstrated is that business/data logic lives *below* both, so a
feature written once (in `crud/` + `models/` + `schemas/`) is reachable from
either surface without duplication.

## Where things go (decision table)

| You are adding…                       | Put it in…            |
|---------------------------------------|-----------------------|
| An HTTP endpoint                      | `api/v1/` + register in `api/main.py` |
| A CLI command                         | `cli/main.py`         |
| A DB table                            | `models/` + Alembic migration |
| Request/response shapes               | `schemas/`            |
| DB queries/writes                     | `crud/`               |
| A client for an external system       | `services/`           |
| A config value, logging change        | `core/`               |
| Engine/session wiring                 | `db/`                 |

If a change seems to need logic in `api/` or `cli/` directly, it usually
belongs one layer down — entry points stay thin so both surfaces stay in sync.

## Package rules

- `__init__.py` files are intentionally empty: they exist only to mark
  packages. Do not add re-exports or import-time side effects to them —
  side effects at import time break test isolation and Alembic's model import.
- All imports absolute (`python_template.…`), enforced habit for the src
  layout. Relative imports (`from ..core import`) are avoided for
  copy-paste clarity in a template.
- Async everywhere for I/O. If you need to call async code from a sync
  context (CLI commands), wrap it with `asyncio.run(...)` inside the command —
  see `cli/main.py` for the established pattern.
