from datetime import timedelta
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.sql.tables import UserJWT
import logging
from app.db.redis.keys import RedisUserKeys
from typing import Any
from config import REFRESH_TOKEN_LIFETIME_DAYS
from shared.config.variables import curretly_msk
from shared.crud.sql.user import UserCrudShared
from app.services.http_client import _http_client
from shared.services.jwt.token import create_default_time_jwt

logger = logging.getLogger(__name__)


class UserProcess(UserCrudShared):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id=user_id, db_session=db_session)

class RedisJsonsProcess(RedisUserKeys):
    def __init__(
        self, 
        user_id: int | str
        ) -> None:
        super().__init__(user_id)