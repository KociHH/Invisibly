from fastapi import HTTPException
import httpx
from typing import Any, Callable, Coroutine
import logging
from config.variables import http_localhosfrom shared.services.http_client.variables import error_handler_wrapper
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

load_dotenv()


class ServiceSecurityHttpClient:
    def __init__(self, security_url: str):
        self.base_url = security_url

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

    async def create_UJWT_post(self, data: dict) -> dict:
        path = "/create_UJWT"
        payload = data
        return await self._perform_request("POST", path, payload)