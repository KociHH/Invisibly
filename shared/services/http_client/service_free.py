from typing import Any
from shared.services.http_client.variables import PublicHttpClient


class ServiceFreeHttpClient(PublicHttpClient):
    def __init__(self, free_url: str):
        super().__init__(free_url)

    async def find_user_by_param(self, param_name: str, param_value: Any) -> dict:
        path = "/find_user_by_param"
        payload = {"param_name": param_name, "param_value": param_value}

        return await self._perform_request("GET", path, payload, None)

    async def get_user_info(
        self, 
        user_id: int | str, 
        w_pswd: bool = False, 
        w_email_hash: bool = False
    ) -> dict:
        path = "/get_user_info"
        payload = {
            "user_id": user_id,
            "w_pswd": w_pswd,
            "w_email_hash": w_email_hash
        }
        return await self._perform_request("GET", path, payload, None)

    async def update_user(
        self,
        data: dict,
        token: str
        ) -> Any | bool: 
        path = "/update_user"
        payload = data
        return await self._perform_request("PATCH", path, payload, token)

    async def get_or_cache_user_info(
        self,
        user_id: int | str,
        handle: str,
        token: str,
        return_items: list | None = None,
        save_sql_redis: bool = True,
    ):
        path = "/get_or_cache_user_info"
        payload = {
            "user_id": user_id,
            "handle": handle,
            "return_items": return_items,
            "save_sql_redis": save_sql_redis
        }
        return await self._perform_request("PATCH", path, payload, token)