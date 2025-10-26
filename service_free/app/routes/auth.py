from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.db.sql.tables import UserRegistered
from app.db.sql.settings import get_db_session
from app.services.http_client import _http_client
from app.crud.user import EncryptEmailProcess
from shared.config.variables import curretly_msk, PSWD_context
from app.services.jwt import create_token
from config import REFRESH_TOKEN_LIFETIME_DAYS
from app.schemas.auth import UserRegister, UserLogin
from app.schemas.response_model import AuthResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# register
@router.post("/register", response_model=AuthResponse)
async def register(
    user: UserRegister, 
    db_session: AsyncSession = Depends(get_db_session)
    ):
    registerb = BaseDAO(UserRegistered, db_session)
    db_login = await registerb.get_one(UserRegistered.login == "@" + user.login)
    if db_login:
        return {"success": False, "message": "Пользователь с таким логином уже существует"}
    
    ee = EncryptEmailProcess(user.email)
    db_email_hash, email_hash = await ee.email_verification(db_session)
    if db_email_hash:
        return {"success": False, "message": "Пользователь с таким email уже существует"}

    password_hash = PSWD_context.hash(user.password)
    new_user = await registerb.create(data={
        "login": "@" + user.login,
        "password": password_hash,
        "name": user.name,
        "email": user.email,
        "email_hash": email_hash,
        "registration_date": curretly_msk(),
    })
    if user.is_registered:
        access_token, _ = create_token(data={"user_id": new_user.user_id}, token_type="access")
        refresh_token, jti = create_token(data={"user_id": new_user.user_id}, token_type="refresh")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid call")
    print(f"access_token: {access_token}\n refresh_token:{refresh_token}")

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

# login
@router.post("/login", response_model=AuthResponse)
async def login(user: UserLogin, db_session: AsyncSession = Depends(get_db_session)):
    loginb = BaseDAO(UserRegistered, db_session)
    db_logging = await loginb.get_one(UserRegistered.login == "@" + user.login)
    
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
