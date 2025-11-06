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

router = APIRouter(prefix="/chats")
logger = logging.getLogger(__name__)


@router.get("/data")
async def user_chats_data(
    user_info: UserProcess = Depends(get_current_user_dep),
):
    rjp = RedisJsonsProcess(user_info.user_id, None, user_info.db_session)
    chats_data = await rjp.get_or_cache_chats_user()
    
    return chats_data 

@router.websocket("/ws")
async def user_chats_ws(
    ws: WebSocket,
    db_session: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(get_user_from_ws)
):    
    try:
        user_info = UserProcess(user_id, db_session)
        
        await wsc.connect(user_info.user_id, ws)
        
        try:
            await wsc.update_chats_for_users([user_info.user_id], db_session)
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
