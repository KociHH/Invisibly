from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import UserLogin, UserRegister
from app.crud.user import EncryptEmailProcess, UserRegisteredCrud
from app.services.jwt import create_token
from shared.config.variables import PSWD_context, curretly_msk
from app.services.http_client import _http_client
import logging
from app.crud.create import CreateCrud

logger = logging.getLogger(__name__)


class Register:
    def __init__(self) -> None:
        pass
    
    async def route(self, user: UserRegister, db_session: AsyncSession):
        user_registered_crud = UserRegisteredCrud(db_session)
        db_login = await user_registered_crud.user_find_by_login("@" + user.login)
        if db_login:
            return {"success": False, "message": "Пользователь с таким логином уже существует"}
    
        ee = EncryptEmailProcess(user.email)
        db_email_hash, email_hash = await ee.email_verification(db_session)
        if db_email_hash:
            return {"success": False, "message": "Пользователь с таким email уже существует"}

        password_hash = PSWD_context.hash(user.password)
        create_crud = CreateCrud(db_session)
        new_user = await create_crud.create_user(
            login = "@" + user.login,
            password = password_hash,
            name = user.name,
            surname = user.surname,
            email = user.email,
            email_hash = email_hash,
        )
        if user.is_registered:
            access_token, _ = create_token(data={"user_id": new_user.user_id}, token_type="access")
            refresh_token, jti = create_token(data={"user_id": new_user.user_id}, token_type="refresh")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid call")
    
        logger.info(f"access_token: {access_token}\n refresh_token:{refresh_token}")

        await _http_client.create_UJWT_post({
            "user_id": new_user.user_id,
            "jti": jti,
            "token_type": "refresh",
        })

        logger.info(
            "\nПользователь был зарегестрирован:\n"
            f"user_id: {new_user.user_id}\n"
            f"login: {user.login}\n"
            f"name: {user.name}\n"
            f"email: {user.email}\n"
            f"registration_date: {curretly_msk()}\n\n"
            )
        return {
            "success": True, 
            "message": "Пользователь успешно зарегистрирован",
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "user_id": new_user.user_id
            }
        
class Login:
    def __init__(self) -> None:
        pass
    
    async def route(self, user: UserLogin, db_session: AsyncSession):
        user_registered_crud = UserRegisteredCrud(db_session)
        db_logging = await user_registered_crud.user_find_by_login("@" + user.login)
    
        if not db_logging:
            return {"success": False, "message": "Неверный логин"}
    
        ee = EncryptEmailProcess(user.email)
        if db_logging.email_hash != ee.hash_email() or not PSWD_context.verify(user.password, db_logging.password):
            return {"success": False, "message": "Неверный email или пароль"}

        access_token, _ = create_token(data={"user_id": db_logging.user_id}, token_type="access")
        refresh_token, jti = create_token(data={"user_id": db_logging.user_id}, token_type="refresh")

        await _http_client.create_UJWT_post({
            "user_id": db_logging.user_id,
            "jti": jti,
            "token_type": "refresh",
        })

        logger.info(
            "\nПользователь вошел в аккаунт:\n"
            f"user_id: {db_logging.user_id}\n"
            f"login: {db_logging.login}\n"
            f"name: {db_logging.name}\n\n"
        )
        return {
            "success": True, 
            "message": "Success login",
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "token_type": "bearer"
            }
        
        
        