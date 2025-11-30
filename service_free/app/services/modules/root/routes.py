from fastapi import APIRouter, HTTPException, Request
import logging
from app.crud.user import GetUserInfo

logger = logging.getLogger(__name__)

class Root:
    def __init__(self) -> None:
        pass
    
    def route(self, request: Request):
        gui = GetUserInfo(request)
        device_inf: dict = gui.get_device_type()

        ip = gui.get_ip_user()
        device_type = device_inf.get('device_type')
        user_agent = device_inf.get("user_agent")
        accept_language = request.headers.get("accept-language")
        cookies = dict(request.cookies)

        user_info = {
            "ip": ip,
            "user_agent": user_agent,
            "device_type": device_type,
            "accept_language": accept_language,
            "cookies": cookies,
            "headers": dict(request.headers),
            "url": str(request.url) 
        }
        logger.info(f'user_info: {user_info}')

        return user_info