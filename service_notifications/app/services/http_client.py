import httpx
from typing import Any, Callable, Coroutine
import logging
from shared.services.http_client.service_free import ServiceFreeHttpClient
from shared.services.http_client.service_friends import ServiceFriendsHttpClient

logger = logging.getLogger(__name__)


class AsyncHttpClient(ServiceFreeHttpClient, ServiceFriendsHttpClient):
    def __init__(self):
        super().__init__()

_http_client = AsyncHttpClient()