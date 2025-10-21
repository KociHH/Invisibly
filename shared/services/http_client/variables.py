from fastapi import HTTPException, Request
import httpx
from typing import Any, Callable, Coroutine
import logging

from shared.crud.redis.usage import create_add_interservice_token

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
    def __init__(self, base_url: str, iss: str, aud: str) -> None:
        self.base_url = base_url
        self.iss = iss
        self.aud = aud

    def template_create_add_interservice_token(self, scopes: list[str]):
        data = {
            "iss": self.iss,
            "aud": self.aud,
            "scopes": scopes
        }
        try:
            token = create_add_interservice_token(data)
            if not token:
                raise HTTPException(status_code=403, detail="This token is already in use")
            return token
        
        except Exception as e:
            logger.error(f"Ошибка в функции create_add_interservice_token: {e}")
            raise HTTPException(status_code=500, detail="Server error")

    @error_handler_wrapper
    async def _perform_request(
        self, 
        method: str, 
        path: str, 
        payload: dict | None,
        interservice_token: str,
        user_token: str | None = None
        ) -> dict:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        headers["Authorization"] = f"Bearer {interservice_token}"
        if user_token:
            headers["X-User-Token"] = f"Bearer {user_token}"

        timeout = httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=2.0)
        limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
        async with httpx.AsyncClient(base_url=self.base_url, timeout=timeout, limits=limits) as client:
            if method == "POST":
                response = await client.post(path, json=payload, headers=headers)
            elif method == "GET":
                response = await client.get(path, params=payload, headers=headers)
            elif method == "PATCH":
                response = await client.patch(path, json=payload, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()

async def get_http_client_state(request: Request) -> PublicHttpClient:
    return request.app.state.http_client

