from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from sqlalchemy import and_
from fastapi import Depends
from app.crud.user import UserProcess, RedisJsonsProcess
from shared.config.variables import path_html
from app.crud.dependencies import  get_current_user_id
from jose import jwt
from shared.data.redis.instance import __redis_save_sql_call__
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.db.sql.settings import get_db_session
from service_notifications.app.db.sql.tables import NotificationSystem, NotificationUser

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/notifications/friends", response_class=HTMLResponse)
async def notifications_friends():
    with open(path_html + "user/notifications/friends.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@router.get("/notifications/friends/data")
async def notifications_friends_data(
    user_info: UserProcess = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_db_session),   
):
    friends_requests_dao = BaseDAO(SendFriendRequests, db_session)
    rjp = RedisJsonsProcess(user_info.user_id, "friends")

    friends_requests_info = await friends_requests_dao.get_all_column_values(
        (SendFriendRequests.request_user_id, SendFriendRequests.send_at),
        SendFriendRequests.user_id == user_info.user_id
    )

    if friends_requests_info:
        result_data = rjp.get_or_cache_friends(db_session, True)

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

    