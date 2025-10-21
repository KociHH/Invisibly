import re
from fastapi import APIRouter, Depends, HTTPException, Request
import logging
from app.crud.user import RedisJsonsProcess
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import UserProcess
from app.db.sql.settings import get_db_session
from app.schemas.data import FriendFilter, FriendFullInfo, FriendUpdate, GetOrCacheFriends
from shared.crud.redis.create import RedisJsonsServerToken
from shared.crud.redis.dependencies import get_interservice_token_info
from shared.services.jwt.token import control_rules_interservice_token
from shared.services.jwt.exceptions import UNAUTHORIZED

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/find_friend_by_param")
async def find_friend_by_param_get(
    uf: FriendFilter = Depends(),
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session),
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
        
        raise HTTPException(status_code=500, detail="Failed to consume token")        
    raise HTTPException(status_code=403, detail="Not enough rights")

@router.get("/get_friend_info")
async def get_friend_info_get(
    ufi: FriendFullInfo = Depends(),
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session),
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
        
        raise HTTPException(status_code=500, detail="Failed to consume token")
    raise HTTPException(status_code=403, detail="Not enough rights")

@router.patch('/update_friend')
async def update_friend_patch(
    user_update: FriendUpdate,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session),
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
            return await user_process.update_friend(user_update.model_dump(exclude_unset=True))
        
        raise HTTPException(status_code=500, detail="Failed to consume token")
    raise HTTPException(status_code=403, detail="Not enough rights")    

@router.patch("/get_or_cache_friends")
async def get_or_cache_friends_patch(
    gocf: GetOrCacheFriends,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["write", "read"])
    except Exception as e:
        logger.warning(f"Проверка межсервисного токена не удалась: {e}")
        raise UNAUTHORIZED
    
    if write and read:
        rjp = RedisJsonsProcess(gocf.user_id, gocf.handle)
        
        consume = token_info.consume_interservice_token()
        if consume:
            return rjp.get_or_cache_friends(db_session, gocf.sort_reverse)
        
        raise HTTPException(status_code=500, detail="Failed to consume token")
    raise HTTPException(status_code=403, detail="Not enough rights")