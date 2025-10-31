from typing import Any
from fastapi import HTTPException, Request
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.db.sql.tables import UserRegistered
import hashlib
import logging
from shared.crud.sql.user import UserCRUD, EncryptEmail
from shared.config.variables import curretly_msk
from shared.crud.redis.create import RedisJsonsUser 
from redis import Redis
from app.db.redis.keys import redis_client, RedisUserKeys

logger = logging.getLogger(__name__)

class UserProcess(UserCRUD):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id, db_session)
        self.user_registered = BaseDAO(UserRegistered, self.db_session)

    async def get_user_info(
        self, 
        w_pswd: bool, 
        w_email_hash: bool, 
        ) -> dict[str, Any] | None:
        try:    
            user_obj = await self.user_registered.get_one(
                UserRegistered.user_id == self.user_id)

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

    async def update_user(
        self, 
        update_data: dict,
        ) -> bool:
        if not update_data: # {}
            logger.error(f"Пустой update_data: {update_data}")
            return False
        
        try:
            success = await self.user_registered.update(
                UserRegistered.user_id == self.user_id, 
                data=update_data
                )
            return success
        except Exception as e:
            logger.error(f"Ошибка при обновлении пользователя {self.user_id}: {e}")
            return False

    @staticmethod
    async def find_user_by_param(
        db_session: AsyncSession,
        param_name: str, 
        param_value: str | Any,
        ) -> dict:
        attr = {
            "user_id": UserRegistered.user_id, 
            "login": UserRegistered.login, 
            "name": UserRegistered.name, 
            'surname': UserRegistered.surname, 
            'password': UserRegistered.password, 
            'email': UserRegistered.email, 
            'email_hash': UserRegistered.email_hash, 
            'registration_date': UserRegistered.registration_date,
            'bio': UserRegistered.bio
            }
        if param_name not in attr:
            logger.error(f"Не найден данный параметр: {param_name}")
            return {'error': f"Param {param_name} not found"}
        
        column_to_search = attr[param_name]

        user_dao = BaseDAO(UserRegistered, db_session)

        user_info = await user_dao.get_one(column_to_search == param_value)
        if user_info:
            return {
                "user_id": user_info.user_id,
                "name": user_info.name,
                "surname": user_info.surname,
                "login": user_info.login,
                "bio": user_info.bio,
                "registration_date": user_info.registration_date,
            }
        return {}


class EncryptEmailProcess(EncryptEmail):
    def __init__(self, email: str,  encrypted: str | None = None) -> None:
        super().__init__(email, encrypted)
        self.email = email
        self.encrypted = encrypted

    async def email_verification(self, db_session: AsyncSession, except_uid: int | str | None = None):
        user_dao = BaseDAO(UserRegistered, db_session)
        email_hash = self.hash_email()

        db_email_hash = await user_dao.get_one(
            and_(UserRegistered.email_hash == email_hash, UserRegistered.user_id != except_uid))

        return db_email_hash, email_hash


class GetUserInfo:
    def __init__(self, request: Request) -> None:
        self.request = request

    def get_ip_user(self) -> str | Any:
        client_ip = (
            self.request.headers.get("x-forwarded-for")
            or self.request.headers.get("x-real-ip")
            or self.request.headers.get("X-Envoy-External-Address")
            or self.request.client.host
        )

        if client_ip and ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()
        return client_ip

    def get_device_type(self) -> dict[str, Any]:
        user_agent = self.request.headers.get("user-agent", "")
        devices = ["Mobi", "Android", "iPhone"]
        device_type = None

        for d in devices:
            if d in user_agent:
                device_type = "mobile"
                break 

        if not device_type:
            device_type = "desktop"
        return {"device_type": device_type, "user_agent": user_agent}


class RedisJsonsProcess(RedisUserKeys):
    def __init__(
        self, 
        user_id: int | str, 
        ) -> None:
        super().__init__(user_id)

    async def get_or_cache_user_info(
        self, 
        db_session: AsyncSession,
        return_items: list | None = None,
        save_sql_redis: bool = True,
        ):
        """
        Берет данные из кеша, если нет данных в `redis` то береться делает запрос к `UserRegistered`
        """
        if return_items == None:
            return_items = ["name", "surname", "login", "bio", "email", "email_hash"]

        obj: dict = self.user_obj.redis_return_data(return_items)

        if obj.get("redis") == "empty":
            user_process = UserProcess(self.user_id, db_session)
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
                new_data = self.user_obj.save_sql_call(new_data)
                error = new_data.get("error")
                if error:
                    logger.error(f"Ошибка в методе save_sql_call: {error}")
                    raise HTTPException(status_code=500, detail="Server error")

            obj = new_data
        return obj

