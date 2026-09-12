# AGENTS.md — Project Root

## What this repository is

This is a **template repository**, not a product. The `Item` feature is a
throwaway demo; the *patterns* (layering, config, auth, pagination, error
handling, testing) are the actual deliverable. When editing, optimize for
"is this a clear example someone will copy?" over "is this the cleverest
implementation?". Every pattern here gets duplicated into downstream projects,
so consistency and simplicity beat sophistication.

## Commands

```bash
uv sync                 # install, incl. dev tools (uv is the package manager; do not use pip/poetry)
make check              # lint + format --check + tests — run this before declaring any change done
make test               # uv run pytest (coverage gate included, see below)
make lint               # uv run ruff check . && uv run ruff format --check .
make format             # uv run ruff format .
make security           # bandit + pip-audit (matches security.yml gates)
make dev                # run the API with hot reload
```

## Hard CI gates (changes fail CI if these break)

1. **Coverage ≥ 80%** — enforced via `addopts` in `pyproject.toml`
   (`--cov-fail-under=80`). Keep `[tool.coverage.run] concurrency = ["greenlet",
   "thread"]` so SQLAlchemy asyncio bodies are counted. New code without tests
   fails the suite locally too.
2. **Ruff lint AND format** — CI runs both `ruff check .` and
   `ruff format --check .`. Always run `make format` after editing.
3. **Bandit (security.yml)** — fails on medium+ severity **and** high+ confidence
   findings in `src/` (`bandit -r src/ -ll -ii`). Bandit is a *separate tool from
   ruff*: bandit suppressions use `# nosec B###`, ruff suppressions use
   `# noqa: RULE`. They are not interchangeable — commit history shows a
   `noqa S104` that had to be changed to `nosec B104` because bandit ignores
   `noqa`. `make security` runs the same bandit gate locally.
4. **pip-audit + trivy** — pip-audit scans the *locked runtime* graph
   (`uv export --frozen --no-dev --no-emit-project`). Adding a runtime dependency
   with a known CVE fails the security workflow. Trivy fs scan fails the job on
   CRITICAL/HIGH (`exit-code: "1"`) and still uploads SARIF.

## Architecture (dependency direction is a rule, not a suggestion)

```
api/ (routers)  cli/ (commands)     <- entry points; thin, no business logic
      │               │
      ▼               ▼
   crud/         services/          <- DB ops / external I/O
      │
      ▼
  models/ (SQLAlchemy)   schemas/ (Pydantic)   <- persistence vs. API contract, kept separate
      │
      ▼
    db/  ← core/ (config, logging; imported by everything, imports nothing internal)
```

- Imports are always absolute: `from python_template.x.y import z`. The
  package lives under `src/` (src layout); tests find it via
  `pythonpath = ["src"]` in `pyproject.toml`.
- Lower layers must never import from higher ones (e.g. `crud/` never imports
  `api/`). `core/` imports nothing from the package except itself.
- Everything I/O-bound is **async** end to end (FastAPI, SQLAlchemy asyncio,
  httpx). Do not introduce sync DB calls or `requests` — a single sync call
  blocks the event loop for all requests.

## Cross-cutting rules

- All runtime configuration goes through `core/config.py` (pydantic-settings).
  Never read `os.environ` directly; never hardcode URLs, keys, or limits.
  When adding a setting, also document it in `.env.example`.
- Schema changes to `models/` require an Alembic migration
  (`uv run alembic revision --autogenerate -m "..."`). See `alembic/AGENTS.md`.
- `test.db` (SQLite) and `.coverage` are generated artifacts, gitignored —
  never commit them.
- Each source directory has its own `AGENTS.md` with the local rules and the
  *why* behind the code. Read it before editing files there, and update it if
  your change alters the rules it states.
