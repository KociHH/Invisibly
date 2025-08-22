from datetime import timedelta
from app.backend.data.pydantic import SuccessAnswer, UserRegister, UserLogin
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.backend.data.sql.tables import UserRegistered, get_db_session
from app.backend.data.sql.utils import CreateSql
from app.backend.utils.user import PSWD_context, path_html, DBUtils, EncryptEmail
from app.backend.utils.dependencies import curretly_msk
from app.backend.jwt.token import create_token
from pydantic import ValidationError
import uuid
from config.env import REFRESH_TOKEN_LIFETIME_DAYS

router = APIRouter()
logger = logging.getLogger(__name__)

# register
@router.get("/register", response_class=HTMLResponse)
async def register_page():
    with open(path_html + "register.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@router.post("/register", response_model=SuccessAnswer)
async def register(user: UserRegister, db_session: AsyncSession = Depends(get_db_session)):
    registerb = BaseDAO(UserRegistered, db_session)
    reg = await registerb.get_one(UserRegistered.login == user.login)
    if reg:
        return {"msg": "Пользователь с таким логином уже существует"}
    
    dbu = DBUtils(db_session)
    db_email_hash, email_hash = await dbu.email_verification(user.email)
    if db_email_hash:
        return {"msg": "Пользователь с таким email уже существует"}

    password_hash = PSWD_context.hash(user.password)
    new_user = await registerb.create(data={
        "login": "@" + user.login,
        "password": password_hash,
        "name": user.name,
        "email": user.email,
        "email_hash": email_hash,
        "registration_date": curretly_msk,
    })
    if user.register:
        access_token, _ = create_token(data={"user_id": new_user.id}, token_type="access")
        refresh_token, jti = create_token(data={"user_id": new_user.id}, token_type="refresh")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный запрос")

    # бд
    issued_at = curretly_msk
    expires_at = curretly_msk + timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS)
    create_sql = CreateSql(db_session)
    await create_sql.create_UJWT(save_elements={
        "user_id": new_user.id,
        "jti": jti,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "token_type": "refresh",
    })

    return {
        "success": True, 
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "user_id": new_user.id
        }

# login
@router.get("/login", response_class=HTMLResponse)
async def login_page():
    with open(path_html + "login.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
    
@router.post("/login", response_model=SuccessAnswer)
async def login(user: UserLogin, db_session: AsyncSession = Depends(get_db_session)):
    loginb = BaseDAO(UserRegistered, db_session)
    log = await loginb.get_one(UserRegistered.login == user.login)
    
    if not log:
        return {"msg": "Неверный логин"}
    
    ee = EncryptEmail(user.email)
    if log.email_hash != ee.hash_email() and not PSWD_context.verify(user.password, log.password):
        return {"msg": "Неверный email или пароль"}
    
    access_token, _ = create_token(data={"user_id": log.id}, token_type="access")
    refresh_token, jti = create_token(data={"user_id": log.id}, token_type="refresh")
    
    # бд
    issued_at = curretly_msk
    expires_at = curretly_msk + timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS)
    create_sql = CreateSql(db_session)
    await create_sql.create_UJWT(save_elements={
        "user_id": log.id,
        "jti": jti,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "token_type": "refresh",
    })

    return {
        "success": True, 
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
        }
