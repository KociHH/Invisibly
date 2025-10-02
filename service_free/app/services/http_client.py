import httpx
from typing import Any, Callable, Coroutine
import logging
from shared.services.http_client.service_security import ServiceSecurityHttpClient
from config import SERVICE_SECURITY_URL

logger = logging.getLogger(__name__)


class AsyncHttpClient(ServiceSecurityHttpClient):
    def __init__(self):
        super().__init__(security_url=SERVICE_SECURITY_URL)

_http_client = AsyncHttpClient()