import httpx
from typing import Any, Callable, Coroutine
import logging
from shared.services.http_client.service_free import ServiceFreeHttpClient
from config import SERVICE_FREE_URL

logger = logging.getLogger(__name__)


class AsyncHttpClient(ServiceFreeHttpClient):
    def __init__(self):
        super().__init__(security_url=SERVICE_FREE_URL)

_http_client = AsyncHttpClient()