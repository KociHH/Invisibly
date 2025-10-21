import httpx
from typing import Any, Callable, Coroutine
import logging
from shared.services.http_client.service_free import ServiceFreeHttpClient
from shared.services.tools.other import get_specific_url

logger = logging.getLogger(__name__)


class AsyncHttpClient(ServiceFreeHttpClient):
    def __init__(self):
        super().__init__(free_url=get_specific_url("FREE"), iss="admin")

_http_client = AsyncHttpClient()