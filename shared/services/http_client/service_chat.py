from typing import Any
from shared.services.http_client.gateway import PublicHttpClient

class ServiceFreeHttpClient(PublicHttpClient):
    def __init__(
        self, 
        free_url: str,
        iss: str,
        aud: str = "chat"
        ):
        super().__init__(free_url, iss, aud)

    async def create_private_chat(
        self,
        user_id1: int | str,
        user_id2: int | str,
        interservice_token: str | None = None,
        user_token: str | None = None
        ):
        """scopes: write"""
        path = "/create_private_chat"
        payload = {
            "user_id1": user_id1,
            "user_id2": user_id2,
        }
        if not interservice_token:
            interservice_token = self.template_create_add_interservice_token(["write"])
        return await self._perform_request("POST", path, payload, interservice_token, user_token)
    
    async def chats_delete(
        self,
        chat_ids: list[str | int],
        calling_user_id: str | int,
        interservice_token: str | None = None,
        user_token: str | None = None
    ):
        """scopes: delete"""
        path = "/chats_delete"
        payload = {
            "chat_ids": chat_ids,
            "calling_user_id": calling_user_id
        }
        if not interservice_token:
            interservice_token = self.template_create_add_interservice_token(["delete"])
        return await self._perform_request("POST", path, payload, interservice_token, user_token)
    
        