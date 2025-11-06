from fastapi import APIRouter, HTTPException, Request
import logging
from app.crud.user import UserProcess, ChatsProcess, RedisJsonsProcess
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from app.db.sql.settings import get_db_session
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from shared.crud.redis.create import RedisJsonsServerToken
from shared.services.jwt.token import control_rules_interservice_token
from shared.crud.redis.dependencies import get_interservice_token_info
from app.schemas.data import CreatePrivateChat, DeleteChat
from shared.services.jwt.exceptions import UNAUTHORIZED
from app.services.websocket import wsc

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create_private_chat")
async def create_private_chat_post(
    cpc: CreatePrivateChat,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    try:
        write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["write"])
    except Exception as e:
        logger.warning(f"Проверка межсервисного токена не удалась: {e}")
        raise UNAUTHORIZED
    
    if write:
        cp = ChatsProcess(cpc.user_id1, db_session)
        
        consume = token_info.consume_interservice_token()
        if consume:
            create = await cp.create_private_chat(cpc.user_id2)
        
            if create:
                chat_id = create.get("chat_id")
                created_at = create.get("created_at")
                participant_user_ids: list = create.get("participant_user_ids", [])
            
                rjp = RedisJsonsProcess(cpc.user_id1, chat_id, db_session)
                rjp.cache_private_chat(created_at, participant_user_ids)

                if participant_user_ids:
                    await wsc.update_chats_for_users(participant_user_ids, db_session)

                return {
                    "success": True,
                    "chat_id": chat_id,
                    "created_at": created_at,
                }
        
        raise HTTPException(status_code=500, detail="Failed to consume token")
    raise HTTPException(status_code=403, detail="Not enough rights")

@router.post("/chats_delete")
async def chats_delete_post(
    dc: DeleteChat,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session)
    ):
    try:
        write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["delete"])
    except Exception as e:
        logger.warning(f"Проверка межсервисного токена не удалась: {e}")
        raise UNAUTHORIZED
    
    if delete:
        consume = token_info.consume_interservice_token()
        if consume:
            rjp = RedisJsonsProcess(dc.calling_user_id, None, db_session)
            
            for chat_id in dc.chat_ids:
                await rjp.delete_chat(chat_id)
                
            return {"success": True}
    
        raise HTTPException(status_code=500, detail="Failed to consume token")
    raise HTTPException(status_code=403, detail="Not enough rights")

