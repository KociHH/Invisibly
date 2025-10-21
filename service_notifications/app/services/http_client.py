import httpx
from typing import Any, Callable, Coroutine
import logging
from shared.services.http_client.service_free import ServiceFreeHttpClient
from shared.services.http_client.service_friends import ServiceFriendsHttpClient
from shared.services.tools.other import get_specific_url

logger = logging.getLogger(__name__)


class AsyncHttpClient(ServiceFreeHttpClient, ServiceFriendsHttpClient):
    def __init__(self):
        self.free = ServiceFreeHttpClient(free_url=get_specific_url("FREE"), iss="notifications")
        self.friends = ServiceFriendsHttpClient(friends_url=get_specific_url("FRIENDS"), iss="notifications")

_http_client = AsyncHttpClient()