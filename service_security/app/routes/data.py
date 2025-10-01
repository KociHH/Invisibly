from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from config.variables import path_html, PSWD_context
from app.crud.user import CreateTable, UserProcess
from app.crud.dependencies import get_current_user_id
from app.db.sql.settings import get_db_session
from app.schemas.data import CreateUJWT

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/create_UJWT")
async def create_UJWT_post(
    cujwt: CreateUJWT,
    user_process: UserProcess = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_db_session)
):
    if user_process.user_id != cujwt.user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

    create_tab = CreateTable(db_session)
    return await create_tab.create_UJWT({
        "user_id": cujwt.user_id,
        "jti": cujwt.jti,
        "token_type": cujwt.token_type,
        "issued_at": cujwt.issued_at,
        "expires_at": cujwt.expires_at,
    })