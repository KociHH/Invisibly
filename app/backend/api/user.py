from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from app.utils import path_html
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from app.backend.data.sql import get_db_session, UserRegistered
from kos_Htools.sql.sql_alchemy import BaseDAO

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/home/{user_id}", response_class=HTMLResponse)
async def user_home(user_id: int, db_session: AsyncSession = Depends(get_db_session)):
    registerb = BaseDAO(UserRegistered, db_session)
    user = await registerb.get_one(UserRegistered.id == user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    with open(path_html + "user_home.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)