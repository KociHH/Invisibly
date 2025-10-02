from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from shared.config.variables import path_html, PSWD_context
from app.crud.user import UserProcess
from app.crud.dependencies import get_current_user_id
from app.db.sql.settings import get_db_session
from app.schemas.data import FriendFilter, FriendFullInfo, FriendUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/find_friend_by_param")
async def find_friend_by_param_get(
    uf: FriendFilter = Depends(),
    user_process: UserProcess = Depends(get_current_user_id),
):
    return await user_process.find_friend_by_param(uf.param_name, uf.param_value)

@router.get("/get_friend_info")
async def get_friend_info_get(
    ufi: FriendFullInfo = Depends(),
    user_process: UserProcess = Depends(get_current_user_id),
):
    if user_process.user_id != ufi.user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

    return await user_process.get_friend_info(ufi.friend_id, ufi.user_id)

@router.patch('/update_friend')
async def update_friend_patch(
    user_update: FriendUpdate,
    user_process: UserProcess = Depends(get_current_user_id),
):
    return await user_process.update_friend(user_update.model_dump(exclude_unset=True))