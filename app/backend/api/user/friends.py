from typing import Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging

from sqlalchemy import and_
from app.backend.utils.user import path_html, UserInfo
from fastapi import Depends
from app.backend.utils.dependencies import  template_not_found_user
from jose import jwt
from app.backend.data.redis.instance import __redis_save_sql_call__
from app.backend.data.redis.utils import RedisJsons
from app.backend.data.redis.utils import redis_return_data
from app.backend.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from app.backend.schemas.user import FriendAdd, UserEditProfileNew, UserProfile
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.backend.data.sql.tables import FriendsUser, SendFriendRequests, UserRegistered, get_db_session
from app.backend.utils.other import full_name_constructor
from config.variables import curretly_msk

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/friends", response_class=HTMLResponse)
async def user_friends():
    with open(path_html + "user/friends/friends.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@router.get("/friends/data", response_model=SuccessAnswer)
async def user_friends_data(
    user_info: UserInfo = Depends(template_not_found_user),
    db_session: AsyncSession = Depends(get_db_session),
    ):
    friends_dao = BaseDAO(FriendsUser, db_session)

    friends = await friends_dao.get_all_column_values(
        (FriendsUser.friend_id, FriendsUser.addition_number),
        FriendsUser.user_id == user_info.user_id
    )

    return_info_friends = {}
    user_dao = BaseDAO(UserRegistered, db_session)

    if friends:
        friends.sort(key=lambda x: x[1], reverse=True)

        for friend_pack in friends:
            friend_id = friend_pack[0]
            addition_number = friend_pack[1]

            friends_info = await user_dao.get_one(
                (UserRegistered.name, UserRegistered.surname),
                UserRegistered.user_id == friend_id,
            )

            full_name = full_name_constructor(friends_info.name, friends_info.surname, str(friend_id))

            return_info_friends[friend_id] = {
                "full_name": full_name,
                "addition_number": addition_number
            }

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
    user_info: UserInfo = Depends(template_not_found_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    user_dao = BaseDAO(UserRegistered, db_session)
    friends_dao = BaseDAO(FriendsUser, db_session)
    friend_requests = BaseDAO(SendFriendRequests, db_session)

    login = "@" + fa.login

    friend_info = await user_dao.get_one(UserRegistered.login == login)
    if friend_info:
        if friend_info.user_id == user_info.user_id:
            return {
                "success": False,
                "message": "You cannot add yourself as a friend"
            }

        friend_user_info = await friends_dao.get_one(
            and_(FriendsUser.user_id == user_info.user_id, FriendsUser.friend_id == friend_info.user_id),
            )

        if friend_user_info:
            return {
                "success": False,
                "message": "This user is already among your friends"
            }
        else:
            friend_requests_info = await friend_requests.get_one(
                and_(SendFriendRequests.request_user_id == user_info.user_id, SendFriendRequests.user_id == friend_info.user_id)
            )

            if friend_requests_info:
                return {
                    "success": False,
                    "message": "You have already sent a request to this user"
                }
            else:
                created = await friend_requests.create({
                    "request_user_id": user_info.user_id,
                    "user_id": friend_info.user_id,
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