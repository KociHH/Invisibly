from fastapi import APIRouter, HTTPException, Request
import logging
from app.crud.user import UserProcess
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from app.db.sql.settings import get_db_session
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from shared.crud.redis.create import RedisJsonsServerToken
from shared.services.jwt.token import control_rules_interservice_token
from shared.crud.redis.dependencies import get_interservice_token_info
from app.schemas.data import AddChatsUser

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/add_chats_user")
async def add_chat_user_post(
    acu: AddChatsUser,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
):
    pass