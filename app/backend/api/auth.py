from app.backend.data.pydantic import UserRegister, UserLogin
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.backend.data.sql import UserRegistered, get_db_session
from app.utils import PSWD_context, path_html

router = APIRouter()
logger = logging.getLogger(__name__)

# register
@router.get("/register", response_class=HTMLResponse)
async def register_page():
    with open(path_html + "register.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@router.post("/register")
async def register(user: UserRegister, db_session: AsyncSession = Depends(get_db_session)):
    registerb = BaseDAO(UserRegistered, db_session)
    reg = await registerb.get_one(UserRegistered.username == user.username)
    if reg:
        return {"msg": "Пользователь с таким именем уже существует"}
    
    ph = PSWD_context.hash(user.password)
    new_user = await registerb.create(data={
        "username": user.username,
        "password": ph,
        "name": user.name
    })
    return {"success": True, "user_id": new_user.id}

# login
@router.get("/login", response_class=HTMLResponse)
async def login_page():
    with open(path_html + "login.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
    
@router.post("/login")
async def login(user: UserLogin, db_session: AsyncSession = Depends(get_db_session)):
    loginb = BaseDAO(UserRegistered, db_session)
    log = await loginb.get_one(UserRegistered.username == user.username)
    
    if not log:
        return {"msg": "Пользователь не найден"}
    
    if not PSWD_context.verify(user.password, log.password):
        return {"msg": "Неверный пароль"}
    
    return {"success": True, "user_id": log.id}
