# AGENTS.md — db/

Database plumbing: the async engine/session factory (`session.py`) and the
declarative base (`base.py`). This directory owns *how* we connect; what the
tables look like lives in `models/`, and what we do with them lives in `crud/`.

## Why it's shaped this way

- **`base.py`** holds only `Base(DeclarativeBase)`. It is deliberately free of
  imports from the rest of the package so that `models/` and `alembic/env.py`
  can both import it without dragging in the engine or settings — Alembic
  needs `Base.metadata` for autogenerate, nothing more.
- **`session.py`** creates one module-level `engine` and `SessionLocal`
  factory per process. `get_db()` is a generator dependency: FastAPI opens a
  session per request and the `async with` guarantees it closes even on
  exceptions. Never open sessions ad hoc elsewhere — request-scoped sessions
  are the transaction boundary the whole CRUD layer assumes.
- SQL echo is controlled by `settings.DB_ECHO` (default off). Turn it on via
  env var when debugging queries; don't hardcode `echo=True`, it floods logs
  and can leak data values into log aggregators.
- The default URL is SQLite via **aiosqlite** because the template must run
  with zero infrastructure. The `+aiosqlite` / `+asyncpg`-style async driver
  suffix in `DATABASE_URL` is mandatory — a sync driver URL will crash
  `create_async_engine`. (`greenlet` in dependencies is required by
  SQLAlchemy's async bridge; don't remove it just because nothing imports it.)

## If you change the database

Swapping SQLite for Postgres should require only a `DATABASE_URL` change
(e.g. `postgresql+asyncpg://...`) plus the driver dependency. Keep it that
way: no SQLite-specific SQL in `crud/`, no dialect-specific column types in
`models/` without a fallback.
