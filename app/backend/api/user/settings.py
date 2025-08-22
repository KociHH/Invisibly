from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from app.backend.utils.user import path_html, UserInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from app.backend.data.sql.tables import get_db_session, UserRegistered
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.backend.utils.dependencies import template_not_found_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/settings", response_class=HTMLResponse)
async def user_settings():
    with open(path_html + "user/settings.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@router.post("/settings")
async def user_settings_post():
    return {}