from datetime import timedelta
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
import hashlib
from typing import Any
from shared.crud.sql.user import UserCrudShared
from shared.crud.sql.user import EncryptEmailShared
from shared.crud.redis.create import RedisJsonsUser
from shared.config.variables import curretly_msk
import logging
from app.services.http_client import _http_client
from redis import Redis
from app.db.redis.keys import redis_client, RedisUserKeys

logger = logging.getLogger(__name__)

class UserProcess(UserCrudShared):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id=user_id, db_session=db_session)


class EncryptEmailProcess(EncryptEmailShared):
    def __init__(self, email: str, encrypted: str | None = None) -> None:
        super().__init__(email, encrypted)
        self.email = email
        self.encrypted = encrypted

    def email_part_encrypt(self) -> str:
        pos_d = self.email.find("@")
        if pos_d == -1:
            return self.email
            
        email_content = self.email[:pos_d]
        email_domain = "@" + self.email[pos_d + 1:]

        size_email_content = len(email_content)
        if size_email_content <= 3:
            return self.email
        
        if size_email_content <= 5:
            return email_content[0] + "*" * (size_email_content - 2) + email_content[-1] + email_domain
        else:
            visible_start = email_content[:2]
            visible_end = email_content[-2:]
            hidden_part = "*" * (size_email_content - 4)
            return visible_start + hidden_part + visible_end + email_domain

    async def email_verification(self, except_uid: int | str | None = None):
        email_hash = self.hash_email()

        db_email_hash = await _http_client.find_user_by_param("email_hash", email_hash) 
        if except_uid:
            if db_email_hash and db_email_hash.get("user_id") == except_uid:
                db_email_hash = None

        return db_email_hash, email_hash


class RedisJsonsProcess(RedisUserKeys):
    def __init__(
        self, 
        user_id: int | str, 
        ) -> None:
        super().__init__(user_id)