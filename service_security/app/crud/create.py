from datetime import timedelta
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
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

class CreateCrud:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session
    
    async def create_UJWT(self, save_elements: dict) -> bool:
        """
        необходимые
        user_id: int
        jti: str
        token_type: str

        опциональные
        revoked: bool = False
        issued_at: datetime = create_default_time_jwt
        expires_at: datetime = create_default_time_jwt
        """
        ujwt = BaseDAO(UserJWT, self.db_session)

        try:
            user_id = save_elements.get("user_id")
            jti = save_elements.get("jti")
            token_type = save_elements.get("token_type")

            if user_id and jti and token_type:
                expires_at = save_elements.get("expires_at")
                issued_at = save_elements.get("issued_at")
                if not expires_at:
                    expires_at, issued_at = create_default_time_jwt(token_type, None)
                revoked = save_elements.get("revoked", False)

                await ujwt.create(data={
                    "user_id": user_id,
                    "jti": jti,
                    "issued_at": issued_at,
                    "expires_at": expires_at,
                    "revoked": revoked,
                    "token_type": token_type
                })
            else:
                logger.warning(f'Необходимо передать (user_id: {user_id} jti: {jti} token_type: {token_type}) значение')
                return False
            
        except Exception as e:
            logger.error(f'Ошибка в функции create_UJWT: {e}')
            return False
        return True
