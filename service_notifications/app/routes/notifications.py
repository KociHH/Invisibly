from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from sqlalchemy import and_
from fastapi import Depends
from app.crud.user import UserProcess, RedisJsonsProcess
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

# friends
@router.get("/notifications/friends/data")
async def notifications_friends_data(
    user_info: UserProcess = Depends(get_current_user_dep),
):
    friends_requests_info = await _http_client.friends.friends_requests_info(user_info.user_id, ["request_user_id", "send_at"])

    if friends_requests_info:
        result_data = await _http_client.friends.get_or_cache_friends(user_info.user_id, "notifications_friends")

        for friend_data in friends_requests_info:
            friend_id = friend_data[0]
            send_at = friend_data[1]
   
            result_data[friend_id] = {
                'send_at': send_at,
            }

    result_data = {
        "success": True,
        "friends_requests": friends_requests_info
    }

    return result_data

# system
@router.get("/notifications/system/data")
async def notifications_friends_data(
    user_info: UserProcess = Depends(get_current_user_dep),
):
    pass