import asyncio
from collections.abc import Callable
from typing import Any

import httpx

_HTTP_CLIENT_ERROR_MIN = 400
_HTTP_SERVER_ERROR_MIN = 500
_HTTP_TOO_MANY_REQUESTS = 429


class RESTClientError(Exception):
    """Base exception for RESTClient errors."""

    def __init__(
        self, message: str, status_code: int | None = None, detail: Any = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class RESTClient:
    def __init__(  # noqa: PLR0913
        self,
        base_url: str,
        transport: httpx.BaseTransport | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
        max_retries: int = 3,
        retry_delay: float = 0.1,  # Default to small delay for template
    ):
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = httpx.AsyncClient(
            base_url=base_url,
            transport=transport,
            headers=headers,
            timeout=timeout,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.client.aclose()

    async def _request_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response: httpx.Response = await func(*args, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Don't retry on most 4xx errors
                if (
                    _HTTP_CLIENT_ERROR_MIN
                    <= e.response.status_code
                    < _HTTP_SERVER_ERROR_MIN
                    and e.response.status_code != _HTTP_TOO_MANY_REQUESTS
                ):
                    detail = ""
                    if "application/json" in e.response.headers.get("content-type", ""):
                        try:
                            detail = e.response.json()
                        except Exception:
                            detail = e.response.text
                    else:
                        detail = e.response.text

                    raise RESTClientError(
                        message=f"API returned error: {e.response.status_code}",
                        status_code=e.response.status_code,
                        detail=detail,
                    ) from e
                last_exception = e
            except (httpx.RequestError, asyncio.TimeoutError) as e:
                last_exception = e

            if attempt < self.max_retries:
                await asyncio.sleep(
                    self.retry_delay * (2**attempt)
                )  # Exponential backoff

        raise RESTClientError(
            message=f"Request failed after {self.max_retries} retries: {last_exception}"
        ) from last_exception

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        return await self._request_with_retry(
            self.client.get, path, params=params, headers=headers
        )

    async def post(
        self,
        path: str,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> Any:
        return await self._request_with_retry(
            self.client.post, path, json=data, headers=headers
        )

    async def put(
        self,
        path: str,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> Any:
        return await self._request_with_retry(
            self.client.put, path, json=data, headers=headers
        )

    async def delete(
        self,
        path: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        return await self._request_with_retry(self.client.delete, path, headers=headers)
