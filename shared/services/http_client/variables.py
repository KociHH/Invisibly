from fastapi import HTTPException
import httpx
from typing import Any, Callable, Coroutine
import logging

logger = logging.getLogger(__name__)

def error_handler_wrapper(func: Coroutine) -> Coroutine:
    async def wrapper(*args, **kwargs) -> dict | Any:
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=500, headers={"error": f"HTTP error: {e.response.status_code}"})
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise HTTPException(status_code=500, headers={"error": f"Request error: {e}"})
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise HTTPException(status_code=500, headers={"error": f"Unexpected error: {e}"})
    return wrapper


class PublicHttpClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    @error_handler_wrapper
    async def _perform_request(self, method: str, path: str, payload: dict | None = None) -> dict:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            if method == "POST":
                response = await client.post(path, json=payload)
            elif method == "GET":
                response = await client.get(path, params=payload)
            elif method == "PATCH":
                response = await client.patch(path, json=payload)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
