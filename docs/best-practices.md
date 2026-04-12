# Best Practices for This Template

This project follows modern Python best practices to ensure maintainability, scalability, and developer productivity.

## Project Structure

- `src/python_template/`: Source code.
  - `api/`: FastAPI routes and application setup.
  - `cli/`: Typer CLI commands.
  - `core/`: Core configuration and shared utilities.
  - `crud/`: Database CRUD operations.
  - `db/`: Database session and base model.
  - `models/`: SQLAlchemy database models.
  - `schemas/`: Pydantic models for data validation.
  - `services/`: Business logic and external service integrations.
- `tests/`: Pytest test suite.
- `docs/`: Documentation and guides.

## Development Standards

- **Configuration:** Use `pydantic-settings` for managing application configuration. Settings are defined in `src/python_template/core/config.py` and can be overridden using environment variables or a `.env` file.
- **Type Hinting:** Use PEP 484 type hints throughout the codebase.
- **Asyncio:** Prefer asynchronous programming for I/O-bound tasks (API, DB, HTTP clients).
- **Validation:** Use Pydantic for all data validation and settings.
- **Dependency Injection:** Use FastAPI's dependency injection for database sessions and services.
- **Linting & Formatting:** Use `ruff` for fast and consistent code style.

## Testing Strategy

- Use `pytest` for all tests.
- Aim for high test coverage across API, CLI, and services.
- Use `pytest-asyncio` for asynchronous test cases.
- Mock external services using `respx` or similar tools.
