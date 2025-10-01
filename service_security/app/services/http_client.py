import httpx
from typing import Any, Callable, Coroutine
import logging
from shared.services.http_client.service_security import ServiceSecurityHttpClient

logger = logging.getLogger(__name__)


class AsyncHttpClient(ServiceSecurityHttpClient):
    def __init__(self):
        super().__init__()

_http_client = AsyncHttpClient()