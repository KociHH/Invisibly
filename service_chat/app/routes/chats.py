from fastapi import APIRouter, HTTPException, Request
import logging
from app.crud.user import UserProcess
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from app.db.sql.settings import get_db_session
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from app.crud.user import ChatsProcess

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/chats/data")
async def user_chats_data(
    user_info: UserProcess = Depends(require_existing_user_dep),
    db_session: AsyncSession = Depends(get_db_session)
):
    cp = ChatsProcess(user_info.user_id)

    chats_data = await cp.get_or_cache_chats(db_session)

    return chats_data 

# @router.post("/chats")
# async def user_chats_post(
#     user_info: UserProcess = Depends(get_current_user_dep),
#     db_session: AsyncSession = Depends(get_db_session)
#     ):
#     pass