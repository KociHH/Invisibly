from fastapi import APIRouter, HTTPException, Request
from shared.services.tools.other import full_name_constructor
from app.services.http_client import _http_client

class FriendProfileData:
    def __init__(self):
        pass
    
    async def route(self, profile_id: str):
        if not profile_id.isdigit:
            raise HTTPException(status_code=405, detail="Page not found")

        friend = False

        user_info = await _http_client.free.find_user_by_param("user_id", profile_id)
        if user_info:
            friend_info = await _http_client.friends.find_friend_by_param("friend_id", profile_id)
        
            if friend_info:
                friend = True

            full_name = full_name_constructor(user_info.get("name"), user_info.get("surname"), str(profile_id))
        
            return {
                "success": True,
                "profile": {
                    "full_name": full_name,
                    "login": user_info.login,
                    "bio": user_info.bio,
                },
                "friend": friend
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
        
class ProcessingFriendProfile:
    def __init__(self):
        pass
    
    async def route(self):
        pass