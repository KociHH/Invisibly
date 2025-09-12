from sqlalchemy.ext.asyncio import AsyncSession
import logging
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.backend.data.sql.tables import SecretKeyJWT, UserJWT
from app.backend.jwt.utils import generate_jwt_secretkey
from config.variables import curretly_msk
from config.env import TOKEN_LIFETIME_DAYS
from datetime import timedelta

logger = logging.getLogger(__name__)

class CreateSql:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session
        
    async def create_UJWT(self, save_elements: dict) -> bool:
        """
        user_id: int
        jti: uuid
        issued_at: date | None
        expires_at: date
        revoked: bool = False
        token_type: str = "refresh"
        """
        ujwt = BaseDAO(UserJWT, self.db_session)

        try:
            user_id = save_elements.get("user_id")
            expires_at = save_elements.get("expires_at", curretly_msk())
            jti = save_elements.get("jti")
            if user_id and expires_at:
                issued_at = save_elements.get("issued_at")
                revoked = save_elements.get("revoked", False)
                token_type = save_elements.get("token_type", "refresh")
                await ujwt.create(data={
                    "user_id": user_id,
                    "jti": jti,
                    "issued_at": issued_at,
                    "expires_at": expires_at,
                    "revoked": revoked,
                    "token_type": token_type
                })
            else:
                logger.warning('Необходимо передать (expires_at, user_id, jti) значение')
                return False
            
        except Exception as e:
            logger.error(f'Ошибка в функции create_UJWT: {e}')
            return False
        return True

    async def create_SKJ(self) -> bool:
        skj = BaseDAO(SecretKeyJWT, self.db_session)
        try:
            new_key = generate_jwt_secretkey(True)
            change_key = curretly_msk() + timedelta(days=TOKEN_LIFETIME_DAYS)
            await skj.create({
                "secret_key": new_key,
                "created_key": curretly_msk(),
                "change_key": change_key,
            })

        except Exception as e:
            logger.error(f"Ошибка при создании jwt токена: {e}")
            return False
        return True