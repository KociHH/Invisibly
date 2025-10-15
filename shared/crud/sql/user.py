from os import urandom
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
import logging
import hashlib
from shared.services.http_client.service_free import ServiceFreeHttpClient

logger = logging.getLogger(__name__)


class UserCRUD:
    def __init__(self, user_id: int | str, db_session: AsyncSession) -> None:
        self.user_id = user_id
        self.db_session = db_session

    async def check_user_existence(
        self, 
        http_client: ServiceFreeHttpClient,
        ):
        """
        Http free service
        """
        return await http_client.get_user_info(self.user_id, False, False)


class EncryptEmail:
    def __init__(self, email: str, encrypted: str | None = None) -> None:
        self.email = email
        self.encrypted = encrypted

    def hash_email(self) -> str:
        return hashlib.sha256(self.email.lower().encode()).hexdigest()
