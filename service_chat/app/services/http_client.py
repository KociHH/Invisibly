import httpx
from typing import Any, Callable, Coroutine
import logging
from config import SERVICE_FREE_URL
from shared.services.http_client.service_free import ServiceFreeHttpClient

logger = logging.getLogger(__name__)


class AsyncHttpClient(ServiceFreeHttpClient):
    def __init__(self):
        super().__init__(free_url=SERVICE_FREE_URL)

_http_client = AsyncHttpClient()