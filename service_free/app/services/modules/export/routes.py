from fastapi import APIRouter, Depends, HTTPException, Query
import logging
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import RedisJsonsProcess, UserProcess
from shared.crud.redis.dependencies import get_interservice_token_info
from app.db.sql.settings import get_db_session
from app.schemas.export import (
    FindUserByParam as scheme_find_user_by_param, 
    UserFullInfo as scheme_user_full_info, 
    UserUpdate as scheme_user_update, 
    GetOrCacheUserInfo as scheme_get_or_cache_user_info)
from shared.crud.redis.create import RedisJsonsServerToken
from shared.services.jwt.token import control_rules_interservice_token
from shared.services.jwt.exceptions import UNAUTHORIZED

logger = logging.getLogger(__name__)


class FindUserByParam:
    def __init__(self) -> None:
        pass
    
    async def route(
        self, 
        fubp: Annotated[scheme_find_user_by_param, Query()],
        token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
        db_session: AsyncSession = Depends(get_db_session),
        ):
        try:
            write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["read"])
        except Exception as e:
            logger.warning(f"Проверка межсервисного токена не удалась: {e}")
            raise UNAUTHORIZED
    
        if read:
            find_user = await UserProcess.find_user_by_param(db_session, fubp.param_name, fubp.param_value)

            consume = token_info.consume_interservice_token()
            if consume:
                return find_user
        
            raise HTTPException(status_code=500, detail="Failed to consume token")
        raise HTTPException(status_code=403, detail="Not enough rights")
    
class GetUserInfo:
    def __init__(self) -> None:
        pass
    
    async def route(
        self,
        ufi: Annotated[scheme_user_full_info, Query()],
        token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
        db_session: AsyncSession = Depends(get_db_session)
    ):
        try:
            write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["read"])
        except Exception as e:
            logger.warning(f"Проверка межсервисного токена не удалась: {e}")
            raise UNAUTHORIZED
    
        if read:
            try:
                uid = int(ufi.user_id) if isinstance(ufi.user_id, str) else ufi.user_id
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid user_id type")

            user_process = UserProcess(uid, db_session)
        
            consume = token_info.consume_interservice_token()
            if consume:
                return await user_process.get_user_info(ufi.w_pswd, ufi.w_email_hash)
        
            raise HTTPException(status_code=500, detail="Failed to consume token")
        raise HTTPException(status_code=403, detail="Not enough rights")
    
class UpdateUser:
    def __init__(self) -> None:
        pass
    
    async def route(
        self,
        uu: scheme_user_update,
        token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
        db_session: AsyncSession = Depends(get_db_session) 
    ):
        try:
            write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["write"])
        except Exception as e:
            logger.warning(f"Проверка межсервисного токена не удалась: {e}")
            raise UNAUTHORIZED
    
        if write:
            try:
                uid = int(uu.check_user_id) if isinstance(uu.check_user_id, str) else uu.check_user_id
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid check_user_id type")

            user_process = UserProcess(uid, db_session)
        
            consume = token_info.consume_interservice_token()
            if consume:
                update_data = uu.model_dump(exclude_unset=True)
                update_data.pop("check_user_id", None)
                return await user_process.update_user(update_data)
        
            raise HTTPException(status_code=500, detail="Failed to consume token")
        raise HTTPException(status_code=403, detail="Not enough rights")
    
class GetOrCacheUserInfo:
    def __init__(self) -> None:
        pass
    
    async def route(
        self,
        gocui: scheme_get_or_cache_user_info,
        token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
        db_session: AsyncSession = Depends(get_db_session)
    ):
        try:
            write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["write", "read"])
        except Exception as e:
            logger.warning(f"Проверка межсервисного токена не удалась: {e}")
            raise UNAUTHORIZED
    
        if write and read:
            rjp = RedisJsonsProcess(gocui.user_id)
        
            consume = token_info.consume_interservice_token()
            if consume:
                return await rjp.get_or_cache_user_info(db_session, gocui.return_items, gocui.save_sql_redis)
        
            raise HTTPException(status_code=500, detail="Failed to consume token")
        raise HTTPException(status_code=403, detail="Not enough rights")