from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from python_template.core.logger import logger


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        logger.error(f"API Error: {exc.message} on {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "status": "error"},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception: {str(exc)} on {request.url}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "status": "error"},
        )
