# AGENTS.md — models/

SQLAlchemy ORM models — the persistence shape of the data. One file per
table/aggregate, each class inheriting `Base` from `db/base.py`.

## Models vs. schemas (the rule people break)

`models/` describes what the **database** stores; `schemas/` describes what
the **API** accepts and returns. They look similar for `Item` only because the
demo is trivial. Never collapse them into one class and never return a model
from an endpoint without a `response_model` schema — the separation is what
lets the DB evolve (add internal columns, soft-delete flags, audit fields)
without changing or leaking through the API contract.

## Rules

- Every model change (new column, new table, type change) requires an Alembic
  migration: `uv run alembic revision --autogenerate -m "..."` then review the
  generated file. Editing a model without a migration means the change exists
  in code but never reaches any database — CI won't catch it, runtime will.
- New models must be imported in `alembic/env.py` (see the
  `import python_template.models.item` line there). Autogenerate only sees
  tables whose modules have been imported; an unimported model silently
  produces an *empty* migration.
- Keep models free of business logic and of imports from `api/`, `crud/`, or
  `schemas/` — models are at the bottom of the dependency graph and anything
  above importing loops back here would create a cycle.
- Index columns you will filter or join on (`index=True` on `id`/`name` in
  `Item` models this). Make nullability explicit — it becomes a DB constraint
  via migration and is hard to tighten later once rows exist.
- `Item` uses the older `Column(...)` declarative style. If you modernize to
  `Mapped[...]`/`mapped_column(...)` (SQLAlchemy 2.0 style, preferred for new
  models), keep the whole file in one style — mixing both confuses readers
  and some tooling.
