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
from app.backend.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from app.backend.schemas.user import UserEditProfileNew, UserProfile
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.backend.data.sql.tables import UserRegistered, get_db_session
from app.backend.utils.other import full_name_constructor

router = APIRouter()
logger = logging.getLogger(__name__)

# profile
@router.get("/profile", response_class=HTMLResponse)
async def user_profile():
    with open(path_html + "user/profile.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    html_content = html_content.replace("{{full_name}}", "")
    html_content = html_content.replace("{{login}}", "")
    html_content = html_content.replace("{{bio_content}}", "")

    return HTMLResponse(content=html_content)

@router.get("/profile/data", response_model=UserProfile)
async def user_profile_data(user_info: UserInfo = Depends(template_not_found_user)):
    user_id = user_info.user_id
    rj = RedisJsons(user_id, "UserRegistered")
    obj: dict = await rj.get_or_cache_user_info(user_info)

    name = obj.get("name", "")
    surname = obj.get("surname", "")

    full_name = full_name_constructor(name, surname, str(user_info.user_id))

    return {
        "user_id": user_id,
        "full_name": full_name,
        "login": obj.get("login") or "N/A",
        "bio": obj.get("bio") or "N/A"
    }

# edit profile
@router.get("/edit_profile", response_class=HTMLResponse)
async def user_edit_profile():
    with open(path_html + "user/edit_profile.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    html_content = html_content.replace("{{name}}", "")
    html_content = html_content.replace("{{surname}}", "")
    html_content = html_content.replace("{{login}}", "")
    html_content = html_content.replace("{{bio_content}}", "")

    return HTMLResponse(content=html_content)

@router.get("/edit_profile/data")
async def user_edit_profile_data(user_info: UserInfo = Depends(template_not_found_user)):
    user_id = user_info.user_id
    rj = RedisJsons(user_id, "UserRegistered")
    obj: dict = await rj.get_or_cache_user_info(user_info)

    login = obj.get("login") or "N/A"
    if login and "@" in login:
        login = login.lstrip("@")

    return {
        "name": obj.get("name") or "N/A",
        "surname": obj.get("surname") or "N/A",
        "login": login,
        "bio": obj.get("bio")
    }

@router.post("/edit_profile", response_model=SuccessMessageAnswer)
async def processing_edit_profile(
    user: UserEditProfileNew, 
    user_info: UserInfo = Depends(template_not_found_user),
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
    userb = BaseDAO(UserRegistered, user_info.db_session)
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
            if field == "login":
                if await userb.get_one(UserRegistered.login == modified_val):
                    return {
                        "success": False,
                        "message": "Этот логин уже занят."
                        }
            update_data[field] = modified_val

    message = "Профиль не был обновлен."
    success = False

    if update_data:
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

    