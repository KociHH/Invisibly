from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from app.utils import PSWD_context, path_html, GetUserInfo

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
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

    with open(path_html + "root.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)