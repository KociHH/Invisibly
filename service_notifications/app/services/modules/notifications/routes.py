from fastapi import APIRouter, HTTPException
import logging
from app.crud.user import UserProcess, RedisJsonsProcess
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)

class NotificationsFriendsData:
    def __init__(self):
        pass
    
    async def route(
        self,
        user_process: UserProcess
    ):
        friends_requests_info = await _http_client.friends.friends_requests_info(user_process.user_id, ["request_user_id", "send_at"])

        if friends_requests_info:
            result_data = await _http_client.friends.get_or_cache_friends(user_process.user_id, "notifications_friends")

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
    
class NotificationsSystemData:
    def __init__(self):
        pass
    
    async def route(
        self,
        user_process: UserProcess
    ):
        pass