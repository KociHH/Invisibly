from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from app.crud.user import UserProcess
from shared.config.variables import path_html
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from service_chat.app.db.sql.settings import get_db_session
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.crud.dependencies import template_not_found_user
from service_chat.app.crud.user import ChatsProcess

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/chats/data")
async def user_chats_data(
    user_info: UserProcess = Depends(template_not_found_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    cp = ChatsProcess(user_info.user_id, "chats")

    chats_data = await cp.get_or_cache_chats(db_session)

    return chats_data 

# @router.post("/chats")
# async def user_chats_post(
#     user_info: UserProcess = Depends(template_not_found_user),
#     db_session: AsyncSession = Depends(get_db_session)
#     ):
#     pass