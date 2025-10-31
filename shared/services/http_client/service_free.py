from typing import Any
from shared.services.http_client.gateway import PublicHttpClient


class ServiceFreeHttpClient(PublicHttpClient):
    def __init__(
        self, 
        free_url: str,
        iss: str,
        aud: str = "free"
        ):
        super().__init__(free_url, iss, aud)
        
    async def find_user_by_param(
        self,
        param_name: str, 
        param_value: Any,
        interservice_token: str | None = None,
        user_token: str | None = None
        ) -> dict:
        """scopes: read"""
        path = "/find_user_by_param"
        payload = {
            "param_name": param_name, 
            "param_value": param_value
        }
        if not interservice_token:
            interservice_token = self.template_create_add_interservice_token(["read"])
        return await self._perform_request("GET", path, payload, interservice_token, user_token)

    async def get_user_info(
        self, 
        user_id: int | str, 
        w_pswd: bool = False, 
        w_email_hash: bool = False,
        interservice_token: str | None = None,
        user_token: str | None = None
    ) -> dict:
        """scopes: read"""
        path = "/get_user_info"
        payload = {
            "user_id": user_id,
            "w_pswd": w_pswd,
            "w_email_hash": w_email_hash
        }
        if not interservice_token:
            interservice_token = self.template_create_add_interservice_token(["read"])
        return await self._perform_request("GET", path, payload, interservice_token, user_token)

    async def update_user(
        self,
        data: dict,
        check_user_id: str | int,
        interservice_token: str | None = None,
        user_token: str | None = None
        ) -> Any | bool: 
        """scopes: write"""
        path = "/update_user"
        data['check_user_id'] = check_user_id
        payload = data
        if not interservice_token:
            interservice_token = self.template_create_add_interservice_token(["write"])
        return await self._perform_request("PATCH", path, payload, interservice_token, user_token)

    async def get_or_cache_user_info(
        self,
        user_id: int | str,
        return_items: list | None = None,
        save_sql_redis: bool = True,
        interservice_token: str | None = None,
        user_token: str | None = None
    ):
        """scopes: read, write"""
        path = "/get_or_cache_user_info"
        payload = {
            "user_id": user_id,
            "return_items": return_items,
            "save_sql_redis": save_sql_redis
        }
        if not interservice_token:
            interservice_token = self.template_create_add_interservice_token(["read", "write"])
        return await self._perform_request("PATCH", path, payload, interservice_token, user_token)