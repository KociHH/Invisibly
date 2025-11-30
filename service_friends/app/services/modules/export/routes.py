from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
import logging
from app.crud.user import RedisJsonsProcess
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import UserProcess
from app.schemas.data import FriendFilter, FriendFullInfo, FriendUpdate, GetOrCacheFriends
from shared.crud.redis.create import RedisJsonsServerToken
from shared.services.jwt.token import control_rules_interservice_token
from shared.services.jwt.exceptions import UNAUTHORIZED
from app.schemas.data import FriendsRequestsInfo

logger = logging.getLogger(__name__)

class FindFriendByParamGet:
    def __init__(self):
        pass
    
    async def route(
        self, 
        uf: Annotated[FriendFilter, Query()],
        token_info: RedisJsonsServerToken,
        db_session: AsyncSession,
    ):
        try:
            write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["read"])
        except Exception as e:
            logger.warning(f"Проверка межсервисного токена не удалась: {e}")
            raise UNAUTHORIZED
    
        if read:
            consume = token_info.consume_interservice_token()
            if consume:
                return await UserProcess.find_friend_by_param(db_session, uf.param_name, uf.param_value)
        
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to consume token")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights")

class GetFriendInfoGet:
    def __init__(self):
        pass
    
    async def route(
        self,
        ufi: Annotated[FriendFullInfo, Query()],
        token_info: RedisJsonsServerToken,
        db_session: AsyncSession,
    ):
        try:
            write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["read"])
        except Exception as e:
            logger.warning(f"Проверка межсервисного токена не удалась: {e}")
            raise UNAUTHORIZED
    
        if read:
            user_process = UserProcess(ufi.user_id, db_session)
        
            consume = token_info.consume_interservice_token()
            if consume:
                return await user_process.get_friend_info(ufi.friend_id, user_process.user_id)
        
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to consume token")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights")
    
class UpdateFriendPatch:
    def __init__(self):
        pass
    
    async def route(
        self,
        user_update: FriendUpdate,
        token_info: RedisJsonsServerToken,
        db_session: AsyncSession,
    ):
        try:
            write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["write"])
        except Exception as e:
            logger.warning(f"Проверка межсервисного токена не удалась: {e}")
            raise UNAUTHORIZED
    
        if write:
            user_process = UserProcess(user_update, db_session)
        
            consume = token_info.consume_interservice_token()
            if consume:
                user_update = user_update.model_dump(exclude_unset=True)
                return await user_process.update_friend(user_update)
        
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to consume token")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights")
 
class GetOrCacheFriendsPatch:
    def __init__(self):
        pass
    
    async def route(
        self,
        gocf: GetOrCacheFriends,
        token_info: RedisJsonsServerToken,
        db_session: AsyncSession,
    ):
        try:
            write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["write", "read"])
        except Exception as e:
            logger.warning(f"Проверка межсервисного токена не удалась: {e}")
            raise UNAUTHORIZED
    
        if write and read:
            rjp = RedisJsonsProcess(gocf.user_id)
        
            consume = token_info.consume_interservice_token()
            if consume:
                return rjp.get_or_cache_friends(db_session, gocf.sort_reverse)
        
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to consume token")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights")
    
class FriendsRequestsInfoGet:
    def __init__(self):
        pass
    
    async def route(
        self,
        fri: Annotated[FriendsRequestsInfo, Query()],
        token_info: RedisJsonsServerToken,
        db_session: AsyncSession,
    ):
        try:
            write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["read"])
        except Exception as e:
            logger.warning(f"Проверка межсервисного токена не удалась: {e}")
            raise UNAUTHORIZED
    
        if read:
            user_process = UserProcess(fri.user_id, db_session)
        
            consume = token_info.consume_interservice_token()
            if consume:
                return await user_process.friends_requests_info(fri.user_id, fri.get_fields)
        
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to consume token")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights")