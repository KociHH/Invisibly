import httpx
from typing import Any, Callable, Coroutine
import logging
from shared.services.http_client.service_security import ServiceSecurityHttpClient
from shared.services.tools.other import get_specific_url

logger = logging.getLogger(__name__)


class AsyncHttpClient(ServiceSecurityHttpClient):
    def __init__(self):
        super().__init__(security_url=get_specific_url("SECURITY"), iss="free")

_http_client = AsyncHttpClient()