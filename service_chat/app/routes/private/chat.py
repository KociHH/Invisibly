from fastapi import APIRouter, HTTPException, Path, Request, WebSocket, WebSocketDisconnect, status
import logging
from app.crud.user import MessageProcess, UserProcess
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.sql.settings import get_db_session
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep, get_user_from_ws
from app.schemas.chat import UserSendMessage
from app.services.modules.chat.service import ChatService

router = APIRouter()
logger = logging.getLogger(__name__)

chat_service = ChatService()

@router.get("/{chat_id}/info")
async def user_chat_info(
    chat_id: str | int = Path(..., title="ID чата"),
    user_info: UserProcess = Depends(get_current_user_dep),
):
    return await chat_service.user_chat_info.route(chat_id, user_info)
    
@router.get("/{chat_id}/history")
async def user_chat_history(
    chat_id: str | int = Path(..., title="ID чата"),
    user_info: UserProcess = Depends(get_current_user_dep),
):
    return await chat_service.user_chat_history.route(chat_id, user_info)
    
@router.post("/message/send")
async def user_send_message(
    usd: UserSendMessage,
    user_info: UserProcess = Depends(get_current_user_dep),
):
    return await chat_service.user_send_message.route(usd, user_info)    

@router.websocket("/ws")
async def user_chats_ws(
    ws: WebSocket,
    db_session: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_user_from_ws)
):    
    return await chat_service.user_chat_ws.route(user_id, db_session, ws)