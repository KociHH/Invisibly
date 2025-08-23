from typing import Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from app.backend.utils.user import path_html, UserInfo
from fastapi import Depends
from app.backend.utils.dependencies import  template_not_found_user
from jose import jwt
from app.backend.data.redis.instance import __redis_save_sql_call__
from app.backend.data.redis.utils import RedisJsons
from app.backend.data.redis.utils import redis_return_data
from app.backend.data.pydantic import SuccessAnswer, SuccessMessageAnswer, UserEditProfileNew, UserProfile
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.backend.data.sql.tables import UserRegistered, get_db_session
from app.backend.utils.other import full_name_constructor

router = APIRouter()
logger = logging.getLogger(__name__)

# profile
@router.get("/profile", response_class=HTMLResponse)
async def user_profile(user_info: UserInfo = Depends(template_not_found_user)):
    with open(path_html + "user/profile.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    user_id = user_info.user_id
    rj = RedisJsons(user_id, "UserRegistered")
    obj: dict = await rj.get_or_cache_user_info(user_info)

    name = obj.get("name")
    surname = obj.get("surname")
    full_name = full_name_constructor(name, surname, "N/A")

    html_content = html_content.replace("{{full_name}}", full_name)
    html_content = html_content.replace("{{login}}", obj.get("login", "N/A"))
    html_content = html_content.replace("{{bio_content}}", obj.get("bio", ""))

    return HTMLResponse(content=html_content)

# edit profile
@router.get("/edit_profile", response_class=HTMLResponse)
async def user_edit_profile(user_info: UserInfo = Depends(template_not_found_user)):
    with open(path_html + "user/edit_profile.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    user_id = user_info.user_id
    rj = RedisJsons(user_id, "UserRegistered")
    obj: dict = await rj.get_or_cache_user_info(user_info)

    html_content = html_content.replace("{{name}}", obj.get("name", "N/A"))
    html_content = html_content.replace("{{surname}}", obj.get("surname", ""))
    html_content = html_content.replace("{{login}}", obj.get("login", "N/A"))
    html_content = html_content.replace("{{bio_content}}", obj.get("bio", ""))

    return HTMLResponse(content=html_content)

@router.post("/edit_profile", response_model=SuccessMessageAnswer)
async def processing_edit_profile(
    user: UserEditProfileNew, 
    user_info: UserInfo = await template_not_found_user()
    ):
    user_id = user.user_id

    if user_id != user_info.user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

    modified_data = {
        "name": user.name,
        "surname": user.surname,
        "login": user.login,
        "bio": user.bio
    }
    rj = RedisJsons(user_id, "UserRegistered")
    obj: dict = await rj.get_or_cache_user_info(user_info)

    now_data = {
        "name": obj.get("name"),
        "surname": obj.get("surname"),
        "login": obj.get("login"),
        "bio": obj.get("bio")
    }

    update_data = {}
    for field, modified_val in modified_data.items():
        old_val = now_data.get(field)
        if modified_val != old_val:
            update_data[field] = modified_val

    message = "profile not updated"
    success = False

    if update_data:
        userb = BaseDAO(UserRegistered, user_info.db_session)
        updated = await userb.update(
            where=UserRegistered.user_id == user_id,
            data=update_data
        )
        
        if updated:
            logger.info(f"Профиль пользователя {user_id} был обновлен")
            message = "profile updated"
            success = True

            saved_data = rj.save_sql_call(
                data=modified_data
            )
            if not saved_data:
                logger.warning(f"Не удалось сохранить в redis для пользователя {user_id}")

    return {
        "success": success,
        "message": message 
    }

    