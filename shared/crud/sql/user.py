from os import urandom
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
import logging
import hashlib

logger = logging.getLogger(__name__)


class UserCRUD:
    def __init__(self, user_id: int | str, db_session: AsyncSession) -> None:
        self.user_id = user_id
        self.db_session = db_session
        self._user_geted_data: bool | Any = False

    def check_user(self) -> bool:
        if not self._user_geted_data:
            return False
        return True


class EncryptEmail:
    def __init__(self, email: str, encrypted: str | None = None) -> None:
        self.email = email
        self.encrypted = encrypted

    def hash_email(self) -> str:
        return hashlib.sha256(self.email.lower().encode()).hexdigest()
