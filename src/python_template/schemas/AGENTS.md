# AGENTS.md — schemas/

Pydantic models defining the **API contract**: what requests must contain and
what responses are allowed to expose. These are the validation and
serialization boundary — nothing enters or leaves the API without passing
through a schema. See `models/AGENTS.md` for why these stay separate from the
ORM models.

## The Base/Create/Update/Read pattern (`item.py`)

Every resource gets four schemas, and the split encodes real API semantics:

- `XBase` — fields shared by all variants.
- `XCreate` — what clients must send to create. Required fields are required
  *here* (e.g. `name`).
- `XUpdate` — every field optional. This, combined with
  `exclude_unset=True` in `crud/`, is what makes updates partial: a client
  can send only the fields it wants to change. Making a field required on
  the update schema silently forces clients to resend everything.
- `X` (read) — what responses contain, including server-generated fields
  (`id`). Carries `model_config = ConfigDict(from_attributes=True)`, which is
  what allows FastAPI to build it from an ORM object; forget it and every
  endpoint returning that resource 500s at serialization time.

Fields left out of the read schema are **stripped from responses** — that is
the mechanism for keeping internal columns private, so choose read-schema
fields deliberately.

## common.py

`PaginatedResponse[T]` is the single, generic envelope for every list
endpoint (`items`, `total`, `page`, `size`, `pages`). It's generic precisely
so new resources reuse it (`PaginatedResponse[Thing]`) instead of inventing a
new pagination shape — one pagination contract across the whole API is the
point. Changing its field names is a breaking change for all list endpoints
and the CLI, which reads `items`/`total` by key.

## Rules

- Pydantic v2 idioms only: `model_config = ConfigDict(...)`, `model_dump()`.
  Do not reintroduce v1 forms (`class Config:`, `.dict()`, `orm_mode`).
- Schemas validate and shape data; they contain no I/O, no DB imports, no
  business logic. They may be imported by any layer, so they must depend on
  nothing but Pydantic.
- Prefer constrained types (`Field(min_length=...)`, `ge=`, etc.) over
  validating in route handlers — validation in the schema is self-documenting
  in OpenAPI and applies everywhere the schema is used.
