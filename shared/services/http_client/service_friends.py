from typing import Any
from shared.services.http_client.variables import PublicHttpClient


class ServiceFriendsHttpClient(PublicHttpClient):
    def __init__(self, friends_url: str):
        super().__init__(friends_url)

    async def find_friend_by_param(self, param_name: str, param_value: Any) -> dict:
        path = "/find_user_by_param"
        payload = {"param_name": param_name, "param_value": param_value}
        return await self._perform_request("GET", path, payload)

    async def friends_requests_info(self, user_id: str | int, fields: list[str] | None):
        path = "/friends_requests_info"
        payload = {"user_id": user_id, "fields": fields}
        return await self._perform_request("GET", path, payload)

    async def get_or_cache_friends(self, user_id: str | int, handle: str, sort_reverse: bool):
        path = "/get_or_cache_friends"
        payload = {"user_id": user_id, "handle": handle, "sort_reverse": sort_reverse}
        return await self._perform_request("GET", path, payload)