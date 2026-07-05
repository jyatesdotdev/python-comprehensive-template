# AGENTS.md — alembic/

Database migrations. Alembic is the *only* sanctioned way schema changes reach
a database — the app never calls `create_all` at runtime (only tests do, on
throwaway tables). `python-template db init` == `alembic upgrade head`.

## How this env.py differs from stock Alembic (and why)

- **URL comes from app settings, not `alembic.ini`:** `env.py` calls
  `config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)`. This
  keeps one source of truth for the DB location — do not put a real URL back
  into `alembic.ini`; it would silently diverge from what the app uses.
- **Async engine:** the app uses an async driver (`sqlite+aiosqlite`), so
  `run_migrations_online()` goes through `async_engine_from_config` +
  `connection.run_sync(...)`. Keep migrations themselves synchronous (normal
  `op.*` calls); the async wrapper handles the driver.
- **Model imports feed autogenerate:** `import python_template.models.item`
  exists purely so `Base.metadata` is populated. **Every new model module
  must be imported here**, or `--autogenerate` produces an empty (or worse,
  table-dropping) migration without any error.

## Workflow for a schema change

1. Edit/add the model in `src/python_template/models/`.
2. Import the module in `env.py` if it's new.
3. `uv run alembic revision --autogenerate -m "describe the change"`
4. **Read the generated file in `versions/` before committing.** Autogenerate
   misses renames (it emits drop+add, losing data) and server defaults;
   fix by hand. Write a real `downgrade()` — don't leave `pass` in it.
5. Apply with `uv run alembic upgrade head` (or `python-template db init`).

## Rules for `versions/` files

- Never edit or delete a migration that may have been applied somewhere —
  history is append-only; fix mistakes with a *new* migration.
- Never renumber/reorder revisions; `down_revision` links form the chain and
  a broken chain makes every environment unmigratable.
- SQLite (the default DB) can't `ALTER` most things — use
  `op.batch_alter_table(...)` for column changes so migrations work on SQLite
  as well as real databases.
