import secrets

from fastapi import HTTPException, Security, WebSocket, WebSocketException, status
from fastapi.security import APIKeyHeader

from python_template.core.config import DEFAULT_DEV_API_KEY, settings

api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)


def is_valid_api_key(api_key: str | None) -> bool:
    if not api_key:
        return False
    return secrets.compare_digest(api_key, settings.API_KEY)


def ws_origin_allowed(origin: str | None) -> bool:
    # Browser CSWSH always sends Origin. Missing Origin is a non-browser client.
    if origin is None or "*" in settings.CORS_ORIGINS:
        return True
    return origin in settings.CORS_ORIGINS


async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    # compare_digest prevents timing attacks on the key comparison
    if is_valid_api_key(api_key_header):
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
    )


async def require_ws_api_key(websocket: WebSocket) -> str:
    """Header or `api_key` query param (browsers cannot set WS headers)."""
    if not ws_origin_allowed(websocket.headers.get("origin")):
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    api_key = websocket.headers.get(
        settings.API_KEY_NAME
    ) or websocket.query_params.get("api_key")
    if not is_valid_api_key(api_key):
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return api_key


def api_key_is_template_default() -> bool:
    return settings.API_KEY == DEFAULT_DEV_API_KEY
