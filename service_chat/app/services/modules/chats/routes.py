from fastapi import HTTPException, Path, Request, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import RedisJsonsProcess, UserProcess
from app.services.websocket import wsc
import logging

logger = logging.getLogger(__name__)

class UserChatsData:
    def __init__(self) -> None:
        pass
    
    async def route(user_info: UserProcess):
        rjp = RedisJsonsProcess(user_info.user_id, None, user_info.db_session)
        chats_data = await rjp.get_or_cache_chats_user()
    
        return chats_data
    
class UserChatsWs:
    def __init__(self) -> None:
        pass
    
    async def route(user_id: str | int, db_session: AsyncSession, ws: WebSocket):
        try:
            user_info = UserProcess(user_id, db_session)
            
            await wsc.connect(user_info.user_id, ws)
        
            try:
                await wsc.update_chats_for_users([user_info.user_id], user_info.db_session)
            except Exception as e:
                logger.error(f"Ошибка при отправке начальных данных чатов: {e}")
        
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