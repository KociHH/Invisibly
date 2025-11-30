from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from sqlalchemy import and_
from fastapi import Depends
from app.crud.user import UserProcess, RedisJsonsProcess
from app.services.modules.notifications.service import NotificationsService
from shared.config.variables import path_html
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from jose import jwt
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.db.sql.settings import get_db_session
from app.db.sql.tables import NotificationSystem, NotificationUser
from app.services.http_client import _http_client

router = APIRouter()
logger = logging.getLogger(__name__)

notifications_service = NotificationsService()

@router.get("/friends/data")
async def notifications_friends_data(
    user_process: UserProcess = Depends(get_current_user_dep),
):
    return await notifications_service.notifications_friends_data.route(user_process)

@router.get("/system/data")
async def notifications_system_data(
    user_process: UserProcess = Depends(get_current_user_dep),
):
    return await notifications_service.notifications_system_data.route(user_process)