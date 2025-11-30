from fastapi import APIRouter, HTTPException, Path, Request, WebSocket, WebSocketDisconnect, status
import logging
from app.crud.user import MessageProcess, UserProcess
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.sql.settings import get_db_session
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep, get_user_from_ws
from app.crud.user import ChatsProcess, RedisJsonsProcess
from app.services.websocket import wsc
from app.services.modules.chats.service import ChatsService

router = APIRouter(prefix="/chats")
logger = logging.getLogger(__name__)

chats_service = ChatsService()

@router.get("/data")
async def user_chats_data(
    user_info: UserProcess = Depends(get_current_user_dep),
):
    return await chats_service.user_chats_data.route(user_info) 

@router.websocket("/ws")
async def user_chats_ws(
    ws: WebSocket,
    db_session: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_user_from_ws)
):    
    return await chats_service.user_chats_ws.route(user_id, db_session, ws)
