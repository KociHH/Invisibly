from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import logging
from app.schemas.account import SettingsExit
from app.crud.user import RedisJsonsProcess
from config.variables import path_html
from app.crud.user import UserProcess
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.sql.settings import get_db_session
from app.crud.dependencies import template_not_found_user, get_current_user_id

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/settings", response_class=HTMLResponse)
async def user_settings():
    with open(path_html + "user/settings.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    html_content = html_content.replace("{{name}}", "")
    html_content = html_content.replace("{{surname}}", "")
    html_content = html_content.replace("{{login}}", "")
    html_content = html_content.replace("{{bio_content}}", "")

    return HTMLResponse(content=html_content)
    
@router.get("/settings/data")
async def user_settings_data(user_info: UserProcess = Depends(get_current_user_id)):
    user_id = user_info.user_id
    
    rjp = RedisJsonsProcess(user_id, "UserRegistered")
    obj: dict = await rjp.get_or_cache_user_info(user_info)

    return {
        "name": obj.get('name') or "N/A",
        "surname": obj.get('surname') or "N/A",
        "login": obj.get('login') or "N/A",
        "bio": obj.get('bio') or "N/A",
    }

@router.post("/logout")
async def user_logout(
    se: SettingsExit,
    user_info: UserProcess = Depends(template_not_found_user)
    ):
    if se.user_id != user_info.user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only logout from your own account")

    return {"success": True}

