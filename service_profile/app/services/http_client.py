import httpx
from typing import Any, Callable, Coroutine
import logging
from shared.services.http_client.service_free import ServiceFreeHttpClient
from shared.services.http_client.service_friends import ServiceFriendsHttpClient
from config import SERVICE_FRIENDS_URL, SERVICE_FREE_URL

logger = logging.getLogger(__name__)


class AsyncHttpClient(ServiceFreeHttpClient, ServiceFriendsHttpClient):
    def __init__(self):
        super.__init__(free_url=SERVICE_FREE_URL, friends_url=SERVICE_FRIENDS_URL)

_http_client = AsyncHttpClient()