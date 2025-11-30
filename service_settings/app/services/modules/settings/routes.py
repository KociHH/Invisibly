from fastapi import APIRouter, HTTPException
import logging
from app.schemas.account import SettingsExit
from app.crud.user import UserProcess
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)

class UserSettingsData:
    def __init__(self):
        pass
    
    async def route(
        self,
        user_process: UserProcess
    ):
        user_id = user_process.user_id
    
        obj: dict = await _http_client.get_or_cache_user_info(user_id)

        return {
            "name": obj.get('name') or "",
            "surname": obj.get('surname') or "",
            "login": obj.get('login') or "",
            "bio": obj.get('bio') or "",
        }
        
class UserLogout:
    def __init__(self):
        pass
    
    async def route(
        self,
        se: SettingsExit,
        user_process: UserProcess
    ):
        if se.user_id != user_process.user_id:
            raise HTTPException(status_code=403, detail="Access denied: you can only logout from your own account")

        return {"success": True}