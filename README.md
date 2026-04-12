# Python Project Template

A comprehensive Python project template showcasing best practices and common patterns.

## Features

- **CLI Tool:** Built with [Typer](https://typer.tiangolo.com/).
- **API (REST, SSE, WebSocket):** Built with [FastAPI](https://fastapi.tiangolo.com/).
- **CRUD:** Database interactions with [SQLAlchemy](https://www.sqlalchemy.org/) and [SQLite](https://www.sqlite.org/).
- **REST Client:** Asynchronous HTTP client using [HTTPX](https://www.python-httpx.org/).
- **Linting & Formatting:** Managed by [Ruff](https://beta.ruff.rs/docs/).
- **Testing:** Powered by [Pytest](https://docs.pytest.org/).

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd python-template

# Install dependencies (using uv)
uv sync

# Or using pip
pip install -e .
```

### Usage

#### CLI

```bash
python-template --help
```

#### API Server

```bash
fastapi dev src/python_template/api/main.py
```

## Adding New Features

Refer to the documentation in `docs/` for detailed guides on extending the template.
