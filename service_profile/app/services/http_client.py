import httpx
from typing import Any, Callable, Coroutine
import logging
from shared.services.http_client.service_free import ServiceFreeHttpClient
from shared.services.http_client.service_friends import ServiceFriendsHttpClient
from shared.services.tools.other import get_specific_url

logger = logging.getLogger(__name__)


class AsyncHttpClient(ServiceFreeHttpClient, ServiceFriendsHttpClient):
    def __init__(self):
        self.free = ServiceFreeHttpClient(free_url=get_specific_url("FREE"))
        self.friends = ServiceFriendsHttpClient(friends_url=get_specific_url("FRIENDS"))

    async def get_or_cache_user_info(
        self, 
        user_id: int | str, 
        handle: str, 
        token: str,
        return_items: list | None = None, 
        save_sql_redis: bool = True
        ):
        return await self.free.get_or_cache_user_info(user_id, handle, token, return_items, save_sql_redis)

_http_client = AsyncHttpClient()