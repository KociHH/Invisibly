from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import logging
from app.schemas.account import SettingsExit
from app.crud.user import RedisJsonsProcess
from shared.config.variables import path_html
from app.crud.user import UserProcess
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.sql.settings import get_db_session
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep, oauth2_scheme
from app.services.http_client import _http_client

router = APIRouter()
logger = logging.getLogger(__name__)
    
@router.get("/settings/data")
async def user_settings_data(
    user_info: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    user_id = user_info.user_id
    
    obj: dict = await _http_client.get_or_cache_user_info(user_id, "UserRegistered")

    return {
        "name": obj.get('name') or "N/A",
        "surname": obj.get('surname') or "N/A",
        "login": obj.get('login') or "N/A",
        "bio": obj.get('bio') or "N/A",
    }

@router.post("/logout")
async def user_logout(
    se: SettingsExit,
    user_info: UserProcess = Depends(require_existing_user_dep)
    ):
    if se.user_id != user_info.user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only logout from your own account")

    return {"success": True}

