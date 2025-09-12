from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from app.backend.data.pydantic import SettingsExit
from app.backend.data.redis.utils import RedisJsons, redis_return_data
from app.backend.utils.user import path_html, UserInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from app.backend.data.sql.tables import get_db_session, UserRegistered
from app.backend.utils.dependencies import template_not_found_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/settings", response_class=HTMLResponse)
async def user_settings():
    with open(path_html + "user/settings.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    html_content = html_content.replace("{{name}}", "N/A")
    html_content = html_content.replace("{{surname}}", "N/A")
    html_content = html_content.replace("{{login}}", "N/A")
    html_content = html_content.replace("{{bio_content}}", "N/A")

    return HTMLResponse(content=html_content)
    
@router.get("/settings/data")
async def user_settings_data(user_info: UserInfo = Depends(template_not_found_user)):
    user_id = user_info.user_id
    
    rj = RedisJsons(user_id, "UserRegistered")
    obj: dict = await rj.get_or_cache_user_info(user_info)

    return {
        "name": obj.get('name', "N/A"),
        "surname": obj.get('surname', "N/A"),
        "login": obj.get('login', "N/A"),
        "bio": obj.get('bio', "N/A"),
    }

@router.post("/logout")
async def user_logout(
    se: SettingsExit,
    user_info: UserInfo = Depends(template_not_found_user)
    ):
    if se.user_id != user_info.user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only logout from your own account")

    return {"success": True}

