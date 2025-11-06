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
from service_chat.app.schemas.chat import UserSendMessage
from app.services.http_client import _http_client
from shared.services.tools.other import full_name_constructor

router = APIRouter(prefix="/chat")
logger = logging.getLogger(__name__)


@router.get("/{chat_id}/info")
async def user_chat_info(
    chat_id: str | int = Path(..., title="ID чата"),
    user_info: UserProcess = Depends(get_current_user_dep),
):
    rjp = RedisJsonsProcess(user_info.user_id, chat_id, user_info.db_session)
    
    participans_chat = await rjp.get_or_cache_participans_chat()
    if participans_chat:
        user_id1 = participans_chat[0]
        user_id2 = participans_chat[1]
        rjp.get_or_cache_private_chat()
        companion_id = user_id1 if user_id1 != user_info.user_id else user_id2
        companion_info = await _http_client.get_user_info(companion_id)
        if companion_info:
            full_name = full_name_constructor(companion_info.get('name'), companion_info.get("surname"), companion_id)
            
            result_data = {
                "success": True,
                "title": full_name,
            }
            return result_data
    
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User bad request")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
        
@router.get("/{chat_id}/history")
async def user_chat_histoyr(
    chat_id: str | int = Path(..., title="ID чата"),
    user_info: UserProcess = Depends(get_current_user_dep),
):
    try:
        rjp = RedisJsonsProcess(user_info.user_id, chat_id, user_info.db_session)
    
        history = await rjp.get_or_cache_message_history_private_chat()
        return {
            "success": True,
            "history": history
        }
    
    except Exception as e:
        logger.error(f"Ошибка в функции user_chat_info: {e}")
        raise HTTPException(status_code=500, detail="Server error")
    
@router.post("/message/send")
async def user_send_message(
    usd: UserSendMessage,
    user_info: UserProcess = Depends(get_current_user_dep),
):
    mp = MessageProcess(usd.chat_id, user_info.user_id, user_info.db_session)
    
    message = await mp.create_message(usd.content)
    if message:
        rjp = RedisJsonsProcess(user_info.user_id, usd.chat_id, user_info.db_session)
        message_id = message.get("message_id")
        participant_id = message.get("participant_id")
        content = message.get("content")
        created_at = message.get("created_at")
        send_at = message.get("send_at")
        
        writed_by_id = await rjp.chatp.get_user_id_from_partid(participant_id)    
        
        cached_message = rjp.cache_message(message_id, content, writed_by_id, send_at, created_at)
        return cached_message           


@router.websocket("/ws")
async def user_chats_ws(
    ws: WebSocket,
    db_session: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_user_from_ws)
):    
    try:
        chat_id = ws.query_params.get("chat_id")
        if not chat_id:
            ws.close(reason="Chat_id required")
            logger.error(f"Не передан chat_id в параметрах websocket: {chat_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WS chat_id not found")
        
        user_info = UserProcess(user_id, db_session)
        
        await wsc.connect(user_info.user_id, ws)
        
        try:
            await wsc.update_history_chat_for_users(chat_id, user_info.user_id, db_session)
        except Exception as e:
            logger.error(f"Ошибка при отправке истории чата: {e}")
        
        try:
            while True:
                data = await ws.receive_text()
                if data is None:
                    break
                
        except WebSocketDisconnect:
            pass
        finally:
            await wsc.disconnect(user_info.user_id, ws)
    except Exception as e:
        logger.error(f"Ошибка при подключении WebSocket: {e}")
        try:
            await ws.close(code=1011, reason="Authentication failed")
        except:
            pass