import asyncio

import typer
import uvicorn

from python_template.core.config import settings
from python_template.core.logger import logger, setup_logging
from python_template.services.rest_client import RESTClient

setup_logging()

app = typer.Typer(
    name="python-template",
    help="A CLI tool demonstrating best practices with Typer.",
    add_completion=False,
)


@app.command()
def hello(name: str = typer.Argument(..., help="The name of the person to greet.")):
    """
    Say hello to someone.
    """
    logger.info(f"Greeting user: {name}")
    typer.echo(f"Hello, {name}!")


@app.command()
def info(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output."
    ),
):
    """
    Display information about this template.
    """
    logger.info("Fetching template information.")
    typer.echo("Python Template CLI Tool")
    if verbose:
        logger.debug("Verbose output enabled.")
        typer.echo("Version: 0.1.0")
        typer.echo("Author: Gemini CLI")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="The host to bind the server to."),  # noqa: S104
    port: int = typer.Option(8000, help="The port to bind the server to."),
    reload: bool = typer.Option(True, help="Enable auto-reload on code changes."),
):
    """
    Start the FastAPI server.
    """
    logger.info(f"Starting server at {host}:{port} (reload={reload})")
    uvicorn.run("python_template.api.main:app", host=host, port=port, reload=reload)


@app.command()
def check_health(
    base_url: str = typer.Option(
        "http://localhost:8000", help="The base URL of the API to check."
    ),
):
    """
    Check the health of the API using the REST client.
    """

    async def _check():
        try:
            async with RESTClient(base_url=base_url) as client:
                result = await client.get("/health")
                typer.echo(f"API Status: {result.get('status')}")
                typer.echo(f"Database: {result.get('database')}")
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            typer.echo(f"Error connecting to API: {e}", err=True)

    asyncio.run(_check())


items_app = typer.Typer(help="Manage items via the API.")
app.add_typer(items_app, name="items")


@items_app.command("create")
def items_create(
    name: str = typer.Argument(..., help="The name of the item."),
    description: str | None = typer.Option(None, help="The description of the item."),
    base_url: str = typer.Option(
        "http://localhost:8000", help="The base URL of the API."
    ),
):
    """
    Create a new item via the API.
    """

    async def _create():
        try:
            headers = {settings.API_KEY_NAME: settings.API_KEY}
            async with RESTClient(base_url=base_url, headers=headers) as client:
                item_data = {"name": name, "description": description}
                result = await client.post("/api/v1/items/", data=item_data)
                typer.echo(f"Item created successfully: ID {result.get('id')}")
        except Exception as e:
            logger.error(f"Item creation failed: {e}")
            typer.echo(f"Error: {e}", err=True)

    asyncio.run(_create())


@items_app.command("list")
def items_list(
    base_url: str = typer.Option(
        "http://localhost:8000", help="The base URL of the API."
    ),
):
    """
    List all items via the API.
    """

    async def _list():
        try:
            headers = {settings.API_KEY_NAME: settings.API_KEY}
            async with RESTClient(base_url=base_url, headers=headers) as client:
                result = await client.get("/api/v1/items/")
                items = result.get("items", [])
                total = result.get("total", 0)
                if not items:
                    typer.echo("No items found.")
                else:
                    typer.echo(f"Found {total} items:")
                    for item in items:
                        typer.echo(
                            f"[{item.get('id')}] {item.get('name')}: {item.get('description')}"
                        )
        except Exception as e:
            logger.error(f"Fetching items failed: {e}")
            typer.echo(f"Error: {e}", err=True)

    asyncio.run(_list())


db_app = typer.Typer(help="Manage the database.")
app.add_typer(db_app, name="db")


@db_app.command("init")
def db_init():
    """
    Initialize the database by running all migrations.
    """
    from alembic.config import Config  # noqa: PLC0415

    from alembic import command  # noqa: PLC0415

    logger.info("Initializing database with migrations...")
    try:
        # Load the Alembic configuration
        alembic_cfg = Config("alembic.ini")
        # Run the upgrade command to the latest revision
        command.upgrade(alembic_cfg, "head")
        typer.echo("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        typer.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    app()
