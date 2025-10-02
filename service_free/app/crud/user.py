from typing import Any
from fastapi import Request
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.db.sql.tables import UserRegistered
import hashlib
import logging
from shared.crud.sql.user import UserCRUD, EncryptEmail
from shared.config.variables import curretly_msk

logger = logging.getLogger(__name__)

class UserProcess(UserCRUD):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id, db_session)
        self._cached_user_info = None
        self.user_registered = BaseDAO(UserRegistered, self.db_session)
        self._user_geted_data = self.user_registered.get_one(UserRegistered.user_id == self.user_id)

        super().__init__(user_id=user_id, db_session=db_session)

    async def get_user_info(
        self, 
        w_pswd: bool, 
        w_email_hash: bool, 
        user_id: int | str | None = None
        ) -> dict[str, Any] | None:
        """
        UserRegistered.user_id == user_id
        """
        try:
            if not user_id:
                if not self.check_user():
                    return None
            
                user_obj = self._cached_user_info
                if not user_obj:
                    user_obj = await self._user_geted_data 
                    self._cached_user_info = user_obj
            else:
                user_obj = await self.user_registered.get_one(UserRegistered.user_id == user_id)

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

    async def update_user(self, update_data: dict) -> bool:
        """
        UserRegistered.user_id == self.user_id
        """
        if not update_data: # {}
            return False

        user_dao = BaseDAO(UserRegistered, self.db_session)
        
        try:
            success = await user_dao.update(
                UserRegistered.user_id == self.user_id, 
                **update_data
                )
            return success
        except Exception as e:
            logger.error(f"Ошибка при обновлении пользователя {self.user_id}: {e}")
            return False

    async def find_user_by_param(
        self, 
        param_name: str, 
        param_value: str | Any
        ) -> dict:
        """
        column_to_search == param_value
        """
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

        user_dao = BaseDAO(UserRegistered, self.db_session)

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
        email_hash = self.hash_email(self.email)

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