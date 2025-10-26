from sqlalchemy.ext.asyncio import AsyncSession
import logging
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.services.jwt import generate_jwt_secretkey
from shared.config.variables import curretly_msk
from config import TOKEN_LIFETIME_DAYS
from datetime import timedelta
from app.db.sql.tables import SecretKeyJWT

logger = logging.getLogger(__name__)

class CreateTable:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

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