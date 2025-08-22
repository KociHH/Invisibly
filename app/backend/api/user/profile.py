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
from app.backend.data.pydantic import SuccessMessageAnswer, UserEditProfileNew
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.backend.data.sql.tables import UserRegistered, get_db_session

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/profile", response_class=HTMLResponse)
async def user_profile(user_info: UserInfo = Depends(template_not_found_user)):
    with open(path_html + "user/profile.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    user_id = user_info.user_id
    rj = RedisJsons(user_id, "profile")
    obj: dict = redis_return_data(items=["name", "login", "bio"], key_data=rj.name_key)
    
    if obj.get("redis") == "empty":
        info: dict[str, Any] = await user_info.get_user_info(w_pswd=False, w_email_hash=False)
        bio_content = info.get("bio", "").strip()
        new_data = rj.save_sql_call("profile", {
            "user_id": info.get("user_id"),
            "name": info.get("name"),
            "login": info.get("login"),
            "email": info.get("email"),
            "bio": bio_content,
        })
        if not new_data:
            logger.error("Не вернулось значение, либо ожидалось другое значение в функции save_sql_call")
            raise HTTPException(status_code=500, detail="Server error")
        
        obj = new_data

    html_content = html_content.replace("{{user_name}}", obj.get("name", "N/A"))
    html_content = html_content.replace("{{user_login}}", obj.get("login", "N/A"))
    
    bio = obj.get("bio", "").strip()
    if not bio:
        html_content = html_content.replace("{{bio_content}}", "<a href=\"/edit_profile\">Добавить био</a>")
    else:
        html_content = html_content.replace("{{bio_content}}", f"<h3>{bio}</h3><h4>О себе</h4>")

    return HTMLResponse(content=html_content)


@router.get("/edit_profile", response_class=HTMLResponse)
async def user_edit_profile(user_info: UserInfo = Depends(template_not_found_user)):
    with open(path_html + "user/edit_profile.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    user_id = user_info.user_id
    k = f"{user_id}-edit_profile"

    obj: dict = redis_return_data(items=["name", "login", "bio", "email"], key_data=k)
    if obj.get("redis") == "empty":
        info: dict[str, Any] = await user_info.get_user_info(w_pswd=False, w_email_hash=False)
        rj = RedisJsons(user_id, "edit_profile")
        new_data = rj.save_sql_call("edit_profile", {
            "name": info.get("name"),
            "login": info.get("login"),
            "bio": info.get("bio"),
            "email": info.get("email"),
        })
        if not new_data:
            logger.error("Не вернулось значение, либо ожидалось другое значение в функции save_sql_call")
            raise HTTPException(status_code=500, detail="Server error")
        
        obj = new_data

    html_content = html_content.replace("{{user_bio}}", obj.get("bio", ""))
    html_content = html_content.replace("{{user_name}}", obj.get("name", "N/A"))
    html_content = html_content.replace("{{user_login}}", obj.get("login", "N/A"))
    html_content = html_content.replace("{{user_email}}", obj.get("email", "N/A"))

    return HTMLResponse(content=html_content)

@router.post("/edit_profile", response_model=SuccessMessageAnswer)
async def user_edit_profile_post(user: UserEditProfileNew, db_session: AsyncSession = Depends(get_db_session)):
    user_id = user.user_id
    modified_data = {
        "name": user.name,
        "login": user.login,
        "email": user.email,
        "bio": user.bio
    }
    rj = RedisJsons(user_id, "edit_profile")
    obj: dict = redis_return_data(items=list(modified_data.keys()), key_data=rj.name_key)

    if not obj or obj.get("redis") == "empty":
        user_info: UserInfo = await template_not_found_user()
        user_data = user_info.get_user_info(w_pswd=False, w_email_hash=False)
        old_data = {
            "name": user_data.get("name"),
            "login": user_data.get("login"),
            "email": user_data.get("email"),
            "bio": user_data.get("bio")
        }
    else:
        old_data = {
            "name": obj.get("name"),
            "login": obj.get("login"),
            "email": obj.get("email"),
            "bio": obj.get("bio")
        }

    update_data = {}
    for field, modified_val in modified_data.items():
        old_val = old_data.get(field)
        if modified_val != old_val:
            update_data[field] = modified_val

    message = "profile not updated"
    success = False

    if update_data:
        userb = BaseDAO(UserRegistered, db_session)
        updated = await userb.update(
            where=UserRegistered.user_id == user_id,
            data=update_data
        )
        
        if updated:
            logger.info(f"Профиль пользователя {user_id} был обновлен")
            message = "profile updated"
            success = True

            saved_data = rj.save_sql_call(
                call="edit_profile",
                data=modified_data
            )
            if not saved_data:
                logger.warning(f"Не удалось сохранить в redis для пользователя {user_id}")

    return {
        "success": success,
        "message": message 
    }

    