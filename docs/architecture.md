# Architecture & POCs

This document describes the architectural decisions and how to run the various Proof of Concepts (POCs) provided in this template.

## Architectural Overview

The project follows a modular structure to separate concerns and improve maintainability:

- **`src/python_template/api/`**: Contains the FastAPI application, divided into versions (`v1/`).
- **`src/python_template/cli/`**: Contains the Typer CLI application.
- **`src/python_template/core/`**: Shared core functionality like configuration management (`config.py`) and logging (`logger.py`).
- **`src/python_template/db/`**: Database session management and base classes.
- **`src/python_template/crud/`**, **`src/python_template/models/`**, **`src/python_template/schemas/`**: Traditional CRUD layer.
- **`src/python_template/services/`**: External services or business logic abstractions (e.g., `RESTClient`).

## Running the POCs

### 1. API (REST)
The API is a standard FastAPI application.
- **Run:** `python-template serve` or `fastapi dev src/python_template/api/main.py`.
- **Explore:** Visit `http://127.0.0.1:8000/docs` for Swagger UI.

### 2. CLI Tool
The CLI interacts with the API using a built-in `RESTClient`.
- **Run:** `python-template --help`
- **Example:** `python-template items create "My Item"` (Make sure the server is running).

### 3. CRUD (SQLAlchemy) & Migrations (Alembic)
The project uses SQLite by default with SQLAlchemy as the ORM and Alembic for migrations.
- **Initialize DB:** `python-template db init` (runs all migrations to reach `head`).
- **Create Migration:** `uv run alembic revision --autogenerate -m "Description"`.
- **Implementation:** Check `src/python_template/crud/item.py` and `src/python_template/api/v1/items.py`.

### 4. Authentication (API Key)
The API includes a simple API Key authentication POC.
- **Configuration:** `API_KEY` and `API_KEY_NAME` in `core/config.py`.
- **Default Key:** `default-dev-key` (dev convenience; override `API_KEY` outside local use).
- **Protected Endpoints:** `/api/v1/items/`, `/api/v1/sse`, and `/api/v1/ws/` require the key. `/` and `/health` do not.
- **Usage:** The CLI automatically sends the key from settings. HTTP clients send `X-API-KEY`; browsers on WebSocket use `?api_key=`.

### 5. WebSocket
A basic chat-like WebSocket POC.
- **Endpoint:** `ws://127.0.0.1:8000/api/v1/ws/{client_id}?api_key=default-dev-key`
- **Test:** Use a tool like `websocat` or a simple browser script:
  ```javascript
  const ws = new WebSocket("ws://127.0.0.1:8000/api/v1/ws/1?api_key=default-dev-key");
  ws.onmessage = (event) => console.log(event.data);
  ws.send("Hello!");
  ```

### 6. SSE (Server-Sent Events)
A real-time event stream POC.
- **Endpoint:** `http://127.0.0.1:8000/api/v1/sse`
- **Test:** `curl -H "X-API-KEY: default-dev-key" http://127.0.0.1:8000/api/v1/sse`

### 7. RESTFUL Client/Server Interaction
The project demonstrates how a client (CLI) can interact with a server (API) using an asynchronous client (`httpx`).
- **Client Implementation:** `src/python_template/services/rest_client.py`.
- **Usage Example:** `src/python_template/cli/main.py` uses the `RESTClient` to call the API.
