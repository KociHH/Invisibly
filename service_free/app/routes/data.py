from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from shared.config.variables import path_html, PSWD_context
from app.crud.user import RedisJsonsProcess, UserProcess
from app.crud.dependencies import get_current_user_id
from app.db.sql.settings import get_db_session
from app.schemas.data import UserFilter, UserFullInfo, UserUpdate, GetOrCacheUserInfo

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/find_user_by_param")
async def find_user_by_param_get(
    uf: UserFilter = Depends(),
    user_process: UserProcess = Depends(get_current_user_id),
):
    return await user_process.find_user_by_param(uf.param_name, uf.param_value)

@router.get("/get_user_info")
async def get_user_info_get(
    ufi: UserFullInfo = Depends(),
    user_process: UserProcess = Depends(get_current_user_id),
):
    if user_process.user_id != ufi.user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

    return await user_process.get_user_info(ufi.w_pswd, ufi.w_email_hash, ufi.user_id)

@router.patch('/update_user')
async def update_user_patch(
    uu: UserUpdate,
    user_process: UserProcess = Depends(get_current_user_id),
):
    return await user_process.update_user(uu.model_dump(exclude_unset=True))

@router.patch("/get_or_cache_user_info")
async def get_or_cache_user_info_patch(
    gocui: GetOrCacheUserInfo,
    user_process: UserProcess = Depends(get_current_user_id),
):
    if user_process.user_id != gocui.user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

    rjp = RedisJsonsProcess(user_process.user_id, gocui.handle)
    
    return await rjp.get_or_cache_user_info(user_process.db_session, gocui.return_items, gocui.save_sql_redis)