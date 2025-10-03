from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Query
from fastapi.responses import HTMLResponse
import logging
from sqlalchemy import and_
from fastapi import Depends
from shared.config.variables import path_html, curretly_msk
from app.crud.dependencies import get_current_user_id
from app.services.http_client import _http_client
from shared.data.redis.instance import __redis_save_sql_call__
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from app.schemas.user import FriendAdd, FriendDelete
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.db.sql.settings import get_db_session
from app.db.sql.tables import FriendsUser, SendFriendRequests
from app.crud.user import RedisJsonsProcess, UserProcess

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/friends/data", response_model=SuccessAnswer)
async def user_friends_data(
    user_info: UserProcess = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_db_session),
    ):
    rjp = RedisJsonsProcess(user_info.user_id, "friends")

    return_info_friends = rjp.get_or_cache_friends(db_session, True)

    return {
        "success": True,
        "friends": return_info_friends,
        }


@router.get("/friends/add", response_class=HTMLResponse)
async def friends_add():
    with open(path_html + "user/friends/friends_add.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@router.post("/friends/add")
async def processing_friend_add(
    fa: FriendAdd,
    user_info: UserProcess = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_db_session),
):
    friends_dao = BaseDAO(FriendsUser, db_session)
    friend_requests = BaseDAO(SendFriendRequests, db_session)

    login = "@" + fa.login

    # friend_info = await rpc_client.find_user_by_param(user_info.user_id, "login", param_value=login)
    friend_info = await _http_client.find_user_by_param("login", param_value=login)
    if friend_info and isinstance(friend_info, dict):
        friend_id = friend_info.get("user_id")

        if friend_id == user_info.user_id:
            return {
                "success": False,
                "message": "You cannot add yourself as a friend"
            }

        friend_user_info = await friends_dao.get_one(
            and_(FriendsUser.user_id == user_info.user_id, FriendsUser.friend_id == friend_id),
            )

        if friend_user_info:
            return {
                "success": False,
                "message": "This user is already among your friends"
            }
        else:
            friend_requests_info = await friend_requests.get_one(
                and_(SendFriendRequests.request_user_id == user_info.user_id, SendFriendRequests.user_id == friend_id)
            )

            if friend_requests_info:
                return {
                    "success": False,
                    "message": "You have already sent a request to this user"
                }
            else:
                created = await friend_requests.create({
                    "request_user_id": user_info.user_id,
                    "user_id": friend_id,
                    "send_at": curretly_msk(),
                })

                if created:
                    return {
                        "success": True,
                        "message": "Application sent!"
                    }    
                else:
                    logger.error(f"Не добавилась заявка для юзера {user_info.user_id}")
                    raise HTTPException(status_code=500, detail="Server error")          
    else:
        return {
            'success': False,
            "message": "User not found"
        }


@router.post("/friends/delete")
async def processing_friend_delete(
    fd: FriendDelete,
    user_info: UserProcess = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_db_session),
):
    friend_dao = BaseDAO(FriendsUser, db_session)

    friend_info = await friend_dao.delete(
        and_(FriendsUser.friend_id == fd.user_id, FriendDelete.user_id == user_info.user_id)
    ) 

    if friend_info:
        return {
            "success": True,
            "message": "Your friend has been deleted"
        }
    else:
        return {
            "success": False,
            "message": "Your friend has not been deleted or not found"
        }