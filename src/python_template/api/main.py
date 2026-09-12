from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from python_template.api import exceptions
from python_template.api.dependencies import (
    api_key_is_template_default,
    get_api_key,
    require_ws_api_key,
)
from python_template.api.v1 import items, sse, ws
from python_template.core.config import settings
from python_template.core.logger import logger, setup_logging
from python_template.db.session import engine

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.API_KEY:
        logger.warning("API_KEY is empty; authenticated routes will always 403")
    elif api_key_is_template_default():
        logger.warning(
            "API_KEY is the template default; override it before any non-local deploy"
        )
    logger.info("Starting up API...")
    yield
    logger.info("Shutting down API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    # False while CORS_ORIGINS may be ["*"]: credentials + wildcard reflects Origin.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


exceptions.setup_exception_handlers(app)


app.include_router(
    items.router,
    prefix="/api/v1/items",
    tags=["items"],
    dependencies=[Depends(get_api_key)],
)
app.include_router(
    ws.router,
    prefix="/api/v1",
    tags=["websocket"],
    dependencies=[Depends(require_ws_api_key)],
)
app.include_router(
    sse.router,
    prefix="/api/v1",
    tags=["sse"],
    dependencies=[Depends(get_api_key)],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Python Template API"}


@app.get("/health")
async def health():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected"}
