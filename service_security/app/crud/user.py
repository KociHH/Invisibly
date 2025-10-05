from datetime import timedelta
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.db.sql.tables import UserJWT
import logging
from shared.crud.redis.create import RedisJsons
from shared.data.redis.instance import __redis_save_sql_call__
import smtplib
from email.message import EmailMessage
import random
from typing import Any
from config import REFRESH_TOKEN_LIFETIME_DAYS
from shared.config.variables import curretly_msk
from shared.crud.sql.user import UserCRUD
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)


class UserProcess(UserCRUD):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id=user_id, db_session=db_session)

    async def get_user_info(self, w_pswd: bool, w_email_hash: bool) -> dict[str, Any] | None:
        try:
            if not self.check_user():
                return None
            
            user_obj = self._cached_user_info
            if not user_obj:
                user_obj = await self._user_geted_data 
                self._cached_user_info = user_obj

            info = {
                "user_id": user_obj.user_id,
                "name": user_obj.name,
                "surname": user_obj.surname,
                "login": user_obj.login,
                "bio": user_obj.bio,
                "email": user_obj.email,
                "registration_date": user_obj.registration_date
            }
            if w_pswd:
                info['password'] = user_obj.password
            if w_email_hash:
                info['email_hash'] = user_obj.email_hash

            return info
            
        except Exception as e:
            logger.error(f'Ошибка в get_user_info:\n{e}')
            return None

class CreateTable:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create_UJWT(self, save_elements: dict) -> bool:
        """
        необходимые
        user_id: int

        опциональные
        jti: str = uuid.uuid4()
        revoked: bool = False
        token_type: str = "refresh"
        issued_at: datetime = curretly_msk()
        expires_at: datetime = curretly_msk() + timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS)
        """
        ujwt = BaseDAO(UserJWT, self.db_session)

        try:
            user_id = save_elements.get("user_id")

            if user_id:
                jti = save_elements.get("jti", uuid.uuid4())
                expires_at = save_elements.get("expires_at", curretly_msk() + timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS))
                issued_at = save_elements.get("issued_at", curretly_msk())
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
                logger.warning('Необходимо передать (user_id) значение')
                return False
            
        except Exception as e:
            logger.error(f'Ошибка в функции create_UJWT: {e}')
            return False
        return True


class RedisJsonsProcess(RedisJsons):
    def __init__(self, user_id: int | str, handle: str) -> None:
        super().__init__(user_id, handle)

    async def get_or_cache_user_info(
        self, 
        user_process: UserProcess, 
        return_items: list | None = None,
        save_sql_redis: bool = True,
        ):
        """
        Берет данные из __redis_save_sql_call__, если нет self.name_key в redis то береться из базы UserRegistered
        
        UserProcess: класс UserProcess объект юзера
        """
        if return_items == None:
            return_items = ["name", "surname", "login", "bio", "email", "email_hash"]

        obj: dict = self.redis_return_data(items=return_items, key_data=self.name_key)

        if obj.get("redis") == "empty":
            user = await user_process.get_user_info(w_pswd=False, w_email_hash=False)
            if user is None:
                logger.error(f"Не удалось получить информацию о пользователе {self.user_id} из базы данных.")
                raise HTTPException(status_code=500, detail="Server error: User not found in database.")
            
            new_data = {
                "user_id": user.get("user_id"),
                "name": user.get("name"),
                "surname": user.get("surname"),
                "login": user.get("login"),
                "bio": user.get("bio"),
                "email": user.get("email"),
            }

            if save_sql_redis:
                new_data = self.save_sql_call(new_data)
                if not new_data:
                    logger.error("Не вернулось значение, либо ожидалось другое значение в функции save_sql_call")
                    raise HTTPException(status_code=500, detail="Server error")

            obj = new_data
        return obj