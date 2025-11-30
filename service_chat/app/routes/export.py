from fastapi import APIRouter, HTTPException, Request
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.sql.settings import get_db_session
from shared.crud.redis.create import RedisJsonsServerToken
from shared.crud.redis.dependencies import get_interservice_token_info
from app.schemas.export import CreatePrivateChat, DeleteChat
from app.services.modules.export.service import ExportService

router = APIRouter()
logger = logging.getLogger(__name__)

export_service = ExportService()

@router.post("/create_private_chat")
async def create_private_chat_post(
    cpc: CreatePrivateChat,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    return await export_service.create_private_chat_post.route(cpc, token_info, db_session)

@router.post("/chats_delete")
async def chats_delete_post(
    dc: DeleteChat,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session)
    ):
    return await export_service.chats_delete_post.route(dc, token_info, db_session)

