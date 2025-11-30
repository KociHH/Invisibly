from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Query
from fastapi.responses import HTMLResponse
import logging
from sqlalchemy import and_
from fastapi import Depends
from shared.config.variables import path_html, curretly_msk
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from app.services.http_client import _http_client
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from app.schemas.user import FriendAdd, FriendDelete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.sql.settings import get_db_session
from app.db.sql.tables import FriendUser, SendFriendRequest
from app.crud.user import RedisJsonsProcess, UserFriendUserCrud, UserProcess, UserSendFriendRequestCrud

logger = logging.getLogger(__name__)

class UserFriendsData:
    def __init__(self):
        pass
    
    async def route(
        self,
        user_process: UserProcess,
    ):
        rjp = RedisJsonsProcess(user_process.user_id)

        return_info_friends = await rjp.get_or_cache_friends(user_process.db_session, True)

        return {
            "success": True,
            "friends": return_info_friends,
        }
        
class ProcessingFriendAdd:
    def __init__(self):
        pass
    
    async def route(
        self,
        fa: FriendAdd,
        user_process: UserProcess,
    ):
        user_friend_user_crud = UserFriendUserCrud(user_process.db_session, user_process.user_id)
        user_send_friend_requests_crud = UserSendFriendRequestCrud(user_process.db_session, user_process.user_id)
        
        login = "@" + fa.login

        friend_info = await _http_client.find_user_by_param("login", login)
        if friend_info and isinstance(friend_info, dict):
            friend_id = friend_info.get("user_id")

            if friend_id == user_process.user_id:
                return {
                    "success": False,
                    "message": "You cannot add yourself as a friend"
                }

            friend_user_info = await user_friend_user_crud.get_friend_user(
                and_(FriendUser.user_id == user_process.user_id, FriendUser.friend_id == friend_id),
                )

            if friend_user_info:
                return {
                    "success": False,
                    "message": "This user is already among your friends"
                }
            else:
                friend_requests_info = await user_send_friend_requests_crud.get_friend_request(friend_id)

                if friend_requests_info:
                    return {
                        "success": False,
                        "message": "You have already sent a request to this user"
                    }
                else:
                    created = await user_send_friend_requests_crud.create_request(friend_id)

                    if created:
                        return {
                            "success": True,
                            "message": "Application sent!"
                        }           
        else:
            return {
                'success': False,
                "message": "User not found"
            }
            
class ProcessingFriendDelete:
    def __init__(self):
        pass
    
    async def route(
        self,
        fd: FriendDelete,
        user_process: UserProcess,
    ):
        user_friend_user_crud = UserFriendUserCrud(user_process.db_session, user_process.user_id)
        
        friend_info = await user_friend_user_crud.delete_friend(fd.user_id)

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