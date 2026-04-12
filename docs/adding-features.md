# Adding New Features

Follow these steps to add new functionality to the project.

## Configuration

Settings are managed in `src/python_template/core/config.py`.

### CORS Configuration

The API is configured with `CORSMiddleware`. You can adjust allowed origins in `config.py`:

```python
CORS_ORIGINS: list[str] = ["*"]
```

### API Key Authentication

The `items` endpoints are protected by an API Key.
- Header Name: `X-API-KEY` (configurable via `API_KEY_NAME`)
- Value: `default-dev-key` (configurable via `API_KEY`)

To protect a new router, add the `get_api_key` dependency:

```python
from fastapi import Depends
from python_template.api.dependencies import get_api_key

app.include_router(
    new_router,
    prefix="/api/v1/new",
    dependencies=[Depends(get_api_key)],
)
```

## Adding a New API Endpoint

1. **Define the Schema:** Create a Pydantic model in `src/python_template/schemas/`.
2. **Define the Model (if DB needed):** Create a SQLAlchemy model in `src/python_template/models/`.
3. **Database Migration:** 
   - Run `uv run alembic revision --autogenerate -m "Add new model"`
   - Run `uv run python-template db init` (or `alembic upgrade head`)
4. **Implement CRUD Logic:** Add database operations in `src/python_template/crud/`.
5. **Create the Router:** Define routes in `src/python_template/api/v1/`.
6. **Include the Router:** Register the new router in `src/python_template/api/main.py`.
7. **Add Tests:** Create a test file in `tests/` and verify the endpoint.

### Pagination

Use the `PaginatedResponse` generic schema for list endpoints:

```python
from python_template.schemas.common import PaginatedResponse

@router.get("/", response_model=PaginatedResponse[MySchema])
async def read_items(skip: int = 0, limit: int = 100):
    # ... CRUD logic returns (items, total_count)
    return PaginatedResponse(
        items=items,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=ceil(total / limit)
    )
```

## Adding a New CLI Command

1. **Implement the Command:** Add a new `@app.command()` in `src/python_template/cli/main.py`.
2. **Add Tests:** Verify the command in `tests/test_cli.py`.

### Pre-implemented CLI Commands

- `serve`: Starts the FastAPI server using `uvicorn`.
- `check-health`: Checks the API health status.
- `items`: A group of commands for managing items (requires API Key):
    - `items list`: Lists all items.
    - `items create <name>`: Creates a new item.
- `db init`: Initializes the database by running all Alembic migrations.

## Logging

Use the centralized logger for consistent output:

```python
from python_template.core.logger import logger

logger.info("Informational message")
logger.error("Error message")
logger.debug("Debug message (only shown if LOG_LEVEL is DEBUG)")
```

## Error Handling in API

1. **Use `APIError`:** Raise `APIError` in your routers or CRUD logic for controlled error responses.
2. **Global Handler:** All unhandled exceptions are caught by the global handler, logged, and return a 500 Internal Server Error.

```python
from python_template.api.exceptions import APIError

if not item:
    raise APIError(message="Item not found", status_code=404)
```

## Background Tasks

FastAPI allows you to define tasks to be run after returning a response.

```python
from fastapi import BackgroundTasks

def my_task(data: str):
    # Do something
    pass

@router.post("/")
async def my_endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(my_task, "some data")
    return {"message": "Task started"}
```

## Adding a New External Service

1. **Implement the Service:** Create a new class in `src/python_template/services/`.
2. **Use Dependency Injection:** Inject the service where needed in the API routers.
3. **Add Tests:** Mock the service responses in your tests.
