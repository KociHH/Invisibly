from fastapi import HTTPException, WebSocket, status, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import MessageProcess, RedisJsonsProcess, UserProcess
from app.services.http_client import _http_client
from shared.services.tools.other import full_name_constructor
from app.schemas.chat import UserSendMessage as scheme_send_message
from app.services.websocket import wsc
import logging

logger = logging.getLogger(__name__)


class UserChatInfo:
    def __init__(self) -> None:
        pass
    
    async def route(chat_id: str | int, user_info: UserProcess):
        rjp = RedisJsonsProcess(user_info.user_id, chat_id, user_info.db_session)
    
        participans_chat = await rjp.get_or_cache_participans_chat()
        if participans_chat:
            user_id1 = participans_chat[0]
            user_id2 = participans_chat[1]
            companion_id = user_id1 if user_id1 != user_info.user_id else user_id2
        
            rjp.get_or_cache_private_chat(companion_id)
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
    
class UserChatHistory:
    def __init__(self) -> None:
        pass
    
    async def route(chat_id: str | int, user_info: UserProcess):
        rjp = RedisJsonsProcess(user_info.user_id, chat_id, user_info.db_session)
    
        history = await rjp.get_or_cache_message_history_private_chat()
        return history
    
class UserSendMessage:
    def __init__(self) -> None:
        pass
    
    async def route(self, usd: scheme_send_message, user_info: UserProcess):
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
        
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Message not created")
    
class UserChatWs:
    def __init__(self) -> None:
        pass
    
    async def route(self, user_id: str | int, db_session: AsyncSession, ws: WebSocket):
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