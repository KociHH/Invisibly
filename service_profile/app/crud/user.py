from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from shared.crud.sql.user import UserCRUD
from shared.crud.redis.create import RedisJsonsUser
import logging
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)

class UserProcess(UserCRUD):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id=user_id, db_session=db_session)

class RedisJsonsProcess(RedisJsonsUser):
    def __init__(self, user_id: int | str, handle: str) -> None:
        super().__init__(user_id, handle)