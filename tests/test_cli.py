from unittest.mock import patch
import respx
from httpx import Response
from typer.testing import CliRunner

from python_template.cli.main import app

runner = CliRunner()


def test_hello_command():
    result = runner.invoke(app, ["hello", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.stdout


def test_info_command():
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "Python Template CLI Tool" in result.stdout


def test_info_command_verbose():
    result = runner.invoke(app, ["info", "--verbose"])
    assert result.exit_code == 0
    assert "Version: 0.1.0" in result.stdout


def test_serve_command():
    with patch("uvicorn.run") as mock_run:
        result = runner.invoke(app, ["serve", "--port", "8080", "--no-reload"])
        assert result.exit_code == 0
        mock_run.assert_called_once_with(
            "python_template.api.main:app", host="0.0.0.0", port=8080, reload=False
        )


@respx.mock
def test_check_health_command():
    respx.get("http://localhost:8000/health").mock(
        return_value=Response(200, json={"status": "healthy", "database": "connected"})
    )
    result = runner.invoke(app, ["check-health"])
    assert result.exit_code == 0
    assert "API Status: healthy" in result.stdout
    assert "Database: connected" in result.stdout


@respx.mock
def test_check_health_command_error():
    respx.get("http://localhost:8000/health").mock(return_value=Response(500))
    result = runner.invoke(app, ["check-health"])
    assert "Error connecting to API" in result.stderr


@respx.mock
def test_items_create_command():
    respx.post("http://localhost:8000/api/v1/items/").mock(
        return_value=Response(201, json={"id": 1, "name": "Test Item", "description": "Desc"})
    )
    result = runner.invoke(app, ["items", "create", "Test Item", "--description", "Desc"])
    assert result.exit_code == 0
    assert "Item created successfully: ID 1" in result.stdout


@respx.mock
def test_items_list_command():
    respx.get("http://localhost:8000/api/v1/items/").mock(
        return_value=Response(
            200,
            json={
                "items": [{"id": 1, "name": "Test Item", "description": "Desc"}],
                "total": 1,
                "page": 1,
                "size": 100,
                "pages": 1,
            },
        )
    )
    result = runner.invoke(app, ["items", "list"])
    assert result.exit_code == 0
    assert "Found 1 items:" in result.stdout
    assert "[1] Test Item: Desc" in result.stdout


@respx.mock
def test_items_list_empty_command():
    respx.get("http://localhost:8000/api/v1/items/").mock(
        return_value=Response(
            200,
            json={
                "items": [],
                "total": 0,
                "page": 1,
                "size": 100,
                "pages": 0,
            },
        )
    )
    result = runner.invoke(app, ["items", "list"])
    assert result.exit_code == 0
    assert "No items found." in result.stdout


def test_db_init_command():
    with patch("alembic.command.upgrade") as mock_upgrade:
        with patch("alembic.config.Config") as mock_config:
            result = runner.invoke(app, ["db", "init"])
            assert result.exit_code == 0
            assert "Database initialized successfully." in result.stdout
            mock_upgrade.assert_called_once()
            mock_config.assert_called_once_with("alembic.ini")
