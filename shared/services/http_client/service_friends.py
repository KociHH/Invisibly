from fastapi import HTTPException
import httpx
from typing import Any, Callable, Coroutine
import logging
from shared.services.http_client.variables import error_handler_wrapper
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class ServiceFriendsHttpClient:
    def __init__(self, friends_url: str):
        self.base_url = friends_url

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

    async def find_friend_by_param(self, param_name: str, param_value: Any) -> dict:
        path = "/find_user_by_param"
        payload = {"param_name": param_name, "param_value": param_value}
        return await self._perform_request("GET", path, payload)