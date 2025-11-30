from fastapi import APIRouter, HTTPException, Request
import logging
from app.crud.user import RedisJsonsProcess, UserProcess
from app.schemas.user import UserEditProfileNew, UserProfile
from shared.services.tools.other import full_name_constructor
from app.services.http_client import _http_client

router = APIRouter()
logger = logging.getLogger(__name__)

class UserProfileData:
    def __init__(self):
        pass
    
    async def route(self, user_process: UserProcess):
        user_id = user_process.user_id
        obj: dict = await _http_client.free.get_or_cache_user_info(user_id)

        name = obj.get("name") or ""
        surname = obj.get("surname") or ""

        full_name = full_name_constructor(name, surname, str(user_process.user_id))

        return {
            "user_id": user_id,
            "full_name": full_name,
            "login": obj.get("login") or "",
            "bio": obj.get("bio") or ""
        }
        
class UserEditProfileData:
    def __init__(self):
        pass
    
    async def route(self, user_process: UserProcess):
        user_id = user_process.user_id
        obj: dict = await _http_client.free.get_or_cache_user_info(user_id)

        login = obj.get("login")  or ""
        if login and "@" in login:
            login = login.lstrip("@")

        return {
            "name": obj.get("name") or "",
            "surname": obj.get("surname") or "",
            "login": login,
            "bio": obj.get("bio") or ""
        }
        
class ProcessingEditProfile:
    def __init__(self):
        pass
    
    async def route(
        self, user: UserEditProfileNew, 
        user_process: UserProcess
        ):
        user_id = user.user_id

        if user_id != user_process.user_id:
            raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

        modified_data = {
            "name": user.name,
            "surname": user.surname,
            "login": user.login,
            "bio": user.bio
        }
        obj: dict = await _http_client.free.get_or_cache_user_info(user_id)

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
                    if await _http_client.free.find_user_by_param("login", modified_val):
                        return {
                            "success": False,
                            "message": "Этот логин уже занят."
                            }
                update_data[field] = modified_val

        message = "Профиль не был обновлен."
        success = False

        if update_data:
            updated = await _http_client.free.update_user(update_data, user_id)
        
            if updated:
                logger.info(f"Профиль пользователя {user_id} был обновлен")
                message = "profile updated"
                success = True
                rjp = RedisJsonsProcess(user_id)

                saved_data = rjp.user_obj.save_sql_call(
                    data=modified_data
                )
                error = saved_data.get("error")
                if error:
                    logger.error(f"Ошибка в методе save_sql_call: {error}")
                    raise HTTPException(status_code=500, detail="Server error")

        return {
            "success": success,
            "message": message 
        }