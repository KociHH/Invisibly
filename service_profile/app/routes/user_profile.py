from typing import Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Query
from fastapi.responses import HTMLResponse
import logging
from sqlalchemy import and_
from app.crud.user import UserProcess
from shared.config.variables import path_html
from fastapi import Depends
from app.crud.dependencies import  template_not_found_user, get_current_user_id
from jose import jwt
from shared.data.redis.instance import __redis_save_sql_call__
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.db.sql.settings import get_db_session
from shared.services.tools.other import full_name_constructor
from app.services.http_client import _http_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/user/profile/data")
async def friend_profile_data(
    profile_id: str = Query(..., description='id профиля пользователя'),
    user_info: UserProcess = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_db_session),
):
    if not profile_id.isdigit:
        raise HTTPException(status_code=405, detail="Page not found")

    friend = False

    user_info = await _http_client.find_user_by_param("user_id", profile_id)
    if user_info:
        friend_info = await _http_client.find_friend_by_param("friend_id", profile_id)
        
        if friend_info:
            friend = True

        full_name = full_name_constructor(user_info.get("name"), user_info.get("surname"), str(profile_id))
        
        return {
            "success": True,
            "profile": {
                "full_name": full_name,
                "login": user_info.login,
                "bio": user_info.bio,
            },
            "friend": friend
        }
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/user/profile")
async def processing_friend_profile(
    user_info: UserProcess = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_db_session),
):
    pass