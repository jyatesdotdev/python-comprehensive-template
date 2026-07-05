# AGENTS.md — crud/

Data-access layer: plain async functions that take an explicit `AsyncSession`
and operate on SQLAlchemy models. This layer exists so that *all* SQL lives in
one place, callable from any entry point (API today, CLI or jobs tomorrow) —
route handlers and commands must never build queries themselves.

## Contract every CRUD module follows (copy `item.py`)

- Functions take `db: AsyncSession` as the **first parameter** — sessions are
  injected by the caller (FastAPI's `Depends(get_db)`), never created here.
  Creating sessions inside CRUD would hide transaction boundaries and make
  the functions untestable with a shared fixture session.
- Inputs are Pydantic schemas (`ItemCreate`, `ItemUpdate`), outputs are ORM
  models or `None`/`bool`. **No HTTP concepts here** — "not found" is `None`,
  not an exception. The API layer decides that `None` means 404; a CLI caller
  might decide it means something else. Raising HTTP errors here would couple
  the layer to one entry point.
- Updates use `item.model_dump(exclude_unset=True)` — this is what makes
  PUT partial-update-friendly: only fields the client actually sent are
  applied, so an omitted field is *not* nulled out. Removing `exclude_unset`
  silently changes API semantics.
- List functions return `(items, total)` tuples — the total count comes from
  a separate `select(func.count())` because the paginated page can't tell you
  how many rows exist overall, and the API's `PaginatedResponse` needs it.
- Each write commits (`await db.commit()`) and `refresh`es the instance so
  server-generated fields (autoincrement `id`) are populated on the returned
  object. If you compose multiple CRUD calls into one transaction, that
  composition belongs in a service function that manages the commit itself.

## SQLAlchemy 2.0 async style — do not regress

- Query with `select(Model).where(...)` and `await db.execute(...)`;
  the legacy `db.query(Model)` API is sync-only and must not appear.
- `.scalar_one_or_none()` for maybe-one, `.scalars().all()` for lists.
- No lazy-loading across awaits: with async SQLAlchemy, accessing an unloaded
  relationship outside the session raises. If you add relationships, load them
  eagerly (`selectinload`) in the query.
