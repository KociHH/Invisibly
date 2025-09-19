from os import urandom
from typing import Any
from fastapi import Request
from passlib.context import CryptContext
from sqlalchemy import Column
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.backend.data.sql.tables import UserRegistered
import logging
from kos_Htools.utils.time import DateTemplate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import hashlib

logger = logging.getLogger(__name__)
path_html = "app/frontend/src/html/"

PSWD_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
# cd app/frontend

class DBUtils:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session
        self.user_registered = BaseDAO(UserRegistered, self.db_session)

    async def email_verification(self, email: str, except_uid: int | str | None = None):
        ee = EncryptEmail(email)
        email_hash = ee.hash_email()
        db_email_hash = await self.user_registered.get_one(
            and_(UserRegistered.email_hash == email_hash, UserRegistered.user_id != except_uid))
        return db_email_hash, email_hash


class UserInfo(DBUtils):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(db_session=db_session)
        self.user_id = user_id
        self._user_info_coroutine = self.user_registered.get_one(UserRegistered.user_id == self.user_id)
        self._cached_user_info = None
        
    async def check_user(self) -> bool:
        if self._cached_user_info is None:
            self._cached_user_info = await self._user_info_coroutine

        if not self._cached_user_info:
            return False
        return True
    
    async def get_user_info(self, w_pswd: bool, w_email_hash: bool) -> dict[str, Any] | None:
        try:
            if not await self.check_user():
                return None
            
            user_obj = self._cached_user_info
            if not user_obj:
                user_obj = await self._user_info_coroutine 
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


class EncryptEmail:
    def __init__(self, email: str, encrypted: str | None = None) -> None:
        self.email = email
        self.encrypted = encrypted

    def encrypt_data(self, key: bytes) -> str:
        if len(key) != 32:
            raise ValueError("Ключ должен быть 32 байта для AES-256")
        
        iv = urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(self.email.encode()) + encryptor.finalize()
        encrypted = base64.b64encode(iv + ciphertext).decode('utf-8')
        self.encrypted = encrypted
        return encrypted
    
    def decrypt_data(self, key: bytes) -> str | None:
        if not self.encrypted:
            logger.warning(f'Значение self.encrypted: {self.encrypted}\nРасшифрование не может быть выполнено')
            return None
        if len(key) != 32:
            raise ValueError("Ключ должен быть 32 байта для AES-256")
        
        data = base64.b64decode(self.encrypted)
        iv = data[:16]
        ciphertext = data[16:]
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode()

    def hash_email(self) -> str:
        return hashlib.sha256(self.email.lower().encode()).hexdigest()
    
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

