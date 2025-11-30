from fastapi import APIRouter, HTTPException, Request, status
import logging
from app.crud.user import UserProcess, ChatsProcess, RedisJsonsProcess
from sqlalchemy.ext.asyncio import AsyncSession
from shared.crud.redis.create import RedisJsonsServerToken
from shared.services.jwt.token import control_rules_interservice_token
from app.schemas.export import CreatePrivateChat, DeleteChat
from shared.services.jwt.exceptions import UNAUTHORIZED
from app.services.websocket import wsc

logger = logging.getLogger(__name__)

class CreatePrivateChatPost:
    def __init__(self) -> None:
        pass
    
    async def route(
        self, cpc: CreatePrivateChat, 
        token_info: RedisJsonsServerToken, 
        db_session: AsyncSession,
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
        
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to consume token")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights")
    
class ChatsDeletePost:
    def __init__(self) -> None:
        pass
    
    async def route(
        self, 
        dc: DeleteChat, 
        token_info: RedisJsonsServerToken, 
        db_session: AsyncSession,
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
    
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to consume token")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights")