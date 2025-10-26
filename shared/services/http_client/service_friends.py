from typing import Any
from shared.services.http_client.gateway import PublicHttpClient


class ServiceFriendsHttpClient(PublicHttpClient):
    def __init__(
        self, 
        friends_url: str,
        iss: str,
        aud: str = "friends"
        ):
        super().__init__(friends_url, iss, aud)

    async def find_friend_by_param(
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

    async def friends_requests_info(
        self, 
        user_id: str | int, 
        fields: list[str] | None,
        interservice_token: str | None = None,
        user_token: str | None = None
        ):
        """scopes: read"""
        path = "/friends_requests_info"
        payload = {
            "user_id": user_id, 
            "fields": fields
            }
        if not interservice_token:
            interservice_token = self.template_create_add_interservice_token(["read"])
        return await self._perform_request("GET", path, payload, interservice_token, user_token)

    async def get_or_cache_friends(
        self, 
        user_id: str | int,
        sort_reverse: bool,
        interservice_token: str | None = None,
        user_token: str | None = None
        ):
        """scopes: write, read"""
        path = "/get_or_cache_friends"
        payload = {
            "user_id": user_id, 
            "sort_reverse": sort_reverse
            }
        if not interservice_token:
            interservice_token = self.template_create_add_interservice_token(["write", "read"])
        return await self._perform_request("GET", path, payload, interservice_token, user_token)