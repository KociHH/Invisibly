import logging
from shared.services.http_client.gateway import PublicHttpClient

logger = logging.getLogger(__name__)


class ServiceSecurityHttpClient(PublicHttpClient):
    def __init__(
        self, 
        security_url: str,
        iss: str,
        aud: str = "security"
        ):
        super().__init__(security_url, iss, aud)

    async def create_UJWT_post(
        self, 
        data: dict, 
        interservice_token: str | None = None,
        user_token: str | None = None
        ) -> dict:
        """scopes: write"""
        path = "/create_UJWT"
        payload = data
        if not interservice_token:
            interservice_token = self.template_create_add_interservice_token(["write"])
        return await self._perform_request("POST", path, payload, interservice_token, user_token)