import logging
from shared.services.http_client.variables import PublicHttpClient

logger = logging.getLogger(__name__)


class ServiceSecurityHttpClient(PublicHttpClient):
    def __init__(self, security_url: str):
        super().__init__(security_url)

    async def create_UJWT_post(self, data: dict) -> dict:
        path = "/create_UJWT"
        payload = data
        return await self._perform_request("POST", path, payload, None)