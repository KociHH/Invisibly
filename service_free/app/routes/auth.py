from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.db.sql.tables import UserRegistered
from app.db.sql.settings import get_db_session
from app.services.http_client import _http_client
from app.crud.user import EncryptEmailProcess
from app.services.modules.auth.service import AuthService
from shared.config.variables import curretly_msk, PSWD_context
from app.services.jwt import create_token
from config import REFRESH_TOKEN_LIFETIME_DAYS
from app.schemas.auth import UserRegister, UserLogin
from app.schemas.response_model import AuthResponse

router = APIRouter()
logger = logging.getLogger(__name__)

auth_service = AuthService()

@router.post("/register", response_model=AuthResponse)
async def register(
    user: UserRegister, 
    db_session: AsyncSession = Depends(get_db_session)
    ):
    return await auth_service.register.route(user, db_session)

@router.post("/login", response_model=AuthResponse)
async def login(
    user: UserLogin, 
    db_session: AsyncSession = Depends(get_db_session)
    ):
    return await auth_service.login.route(user, db_session)
