from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from app.schemas.data import FriendsRequestsInfo

from sqlalchemy.ext.asyncio import AsyncSession
from shared.config.variables import path_html, PSWD_context
from app.crud.user import UserProcess
from app.crud.dependencies import get_current_user_id
from app.db.sql.settings import get_db_session
from app.schemas.data import FriendFilter, FriendFullInfo, FriendUpdate

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/friends_requests_info")
async def friends_requests_info_get(
    fri: FriendsRequestsInfo = Depends(),
    user_process: UserProcess = Depends(get_current_user_id),
):
    return await user_process.friends_requests_info(fri.user_id, fri.get_fields)