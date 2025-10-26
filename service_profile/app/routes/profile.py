from typing import Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Query
from fastapi.responses import HTMLResponse
import logging
from fastapi import Depends
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep, oauth2_scheme
from jose import jwt
from app.crud.user import RedisJsonsProcess, UserProcess
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from app.schemas.user import UserEditProfileNew, UserProfile
from shared.services.tools.other import full_name_constructor
from app.services.http_client import _http_client

router = APIRouter()
logger = logging.getLogger(__name__)

# profile
@router.get("/profile/data", response_model=UserProfile)
async def user_profile_data(
    user_process: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    user_id = user_process.user_id
    rjp = RedisJsonsProcess(user_id)
    obj: dict = await _http_client.free.get_or_cache_user_info(user_id, rjp.user_obj.name_key)

    name = obj.get("name") or ""
    surname = obj.get("surname") or ""

    full_name = full_name_constructor(name, surname, str(user_process.user_id))

    return {
        "user_id": user_id,
        "full_name": full_name,
        "login": obj.get("login") or "",
        "bio": obj.get("bio") or ""
    }

# edit profile
@router.get("/edit_profile/data")
async def user_edit_profile_data(
    user_info: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    user_id = user_info.user_id
    obj: dict = await _http_client.free.get_or_cache_user_info(user_id, "UserRegistered")

    login = obj.get("login")  or ""
    if login and "@" in login:
        login = login.lstrip("@")

    return {
        "name": obj.get("name") or "",
        "surname": obj.get("surname") or "",
        "login": login,
        "bio": obj.get("bio") or ""
    }

@router.post("/edit_profile", response_model=SuccessMessageAnswer)
async def processing_edit_profile(
    user: UserEditProfileNew, 
    user_info: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
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
    rjp = RedisJsonsProcess(user_id)
    obj: dict = await _http_client.free.get_or_cache_user_info(user_id, rjp.user_obj.name_key)

    now_data = {
        "name": obj.get("name") or "",
        "surname": obj.get("surname") or "",
        "login": obj.get("login") or "",
        "bio": obj.get("bio") or ""
    }

    update_data = {}
    for field, modified_val in modified_data.items():
        old_val = now_data.get(field)
        if modified_val != old_val:
            if field == "login":
                if await _http_client.find_user_by_param("login", modified_val):
                    return {
                        "success": False,
                        "message": "Этот логин уже занят."
                        }
            update_data[field] = modified_val

    message = "Профиль не был обновлен."
    success = False

    if update_data:
        updated = await _http_client.update_user(update_data)
        
        if updated:
            logger.info(f"Профиль пользователя {user_id} был обновлен")
            message = "profile updated"
            success = True

            saved_data = rjp.user_obj.save_sql_call(
                data=modified_data
            )
            if not saved_data:
                logger.warning(f"Не удалось сохранить в redis для пользователя {user_id}")

    return {
        "success": success,
        "message": message 
    }


