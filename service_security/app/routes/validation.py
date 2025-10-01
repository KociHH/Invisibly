from fastapi import APIRouter, HTTPException, Body
from fastapi.params import Query
from fastapi.responses import HTMLResponse
import logging
import uuid
from fastapi import Depends
from config.variables import path_html, PSWD_context
from app.crud.user import UserProcess
from app.crud.dependencies import template_not_found_user, get_current_user_id
from service_security.app.schemas.code import ResendCode, SendCode
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from app.crud.user import EmailProcess
from app.services.jwt import decode_jwt_token, create_token
from datetime import timedelta
from app.crud.user import RedisJsonsProcess
from shared.data.redis.instance import __redis_save_jwt_token__
from config.variables import curretly_msk

logger = logging.getLogger(__name__)
router = APIRouter()

# email code
@router.get("/confirm_code", response_class=HTMLResponse)
async def confirm_code():
    with open(path_html + "confirm_code.html", "r", encoding="utf-8") as html_file:
        html_content = html_file.read()

    html_content = html_content.replace("{{email}}", "")
    html_content = html_content.replace("{{life_time}}", "")
    html_content = html_content.replace("{{life_time_repeated_code}}", "")

    return HTMLResponse(content=html_content)

@router.get("/confirm_code/data")
# 1. /confirm_code?cause=... 2. /confirm_code?cause=...&resend=...?
async def confirm_code_data(
    rc: ResendCode = Depends(),
    cause: str = Query(..., description="Причина вызова confirm_code"),
    user_info: UserProcess = Depends(get_current_user_id),
    ):
    
    send_code = False

    rjp = RedisJsonsProcess(user_info.user_id, cause)
    user = await rjp.get_or_cache_user_info(user_info, ["email"], False)
    if user:
        email = user.get("email")

    if not email or not user:
        logger.error(f"Не найден email пользователя либо он сам {user_info.user_id}")
        raise HTTPException(status_code=500, detail="Server error")
    
    redis_data: dict | None = __redis_save_jwt_token__.get_cached()
    token_info = redis_data.get(rjp.name_key)

    new_email: str | None = None

    if token_info:
        try:
            old_token = token_info.get("token")
            used: bool = token_info.get("used", False)
            old_verification_token = decode_jwt_token(old_token)
            user_id = old_verification_token.get("user_id")
            
            if user_info.user_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

            code = old_verification_token.get("verification_code")
            new_email = old_verification_token.get("new_email")
            if not code or not new_email:
                logger.error(f'Код либо new_email не найден из токена: {code}')
                raise HTTPException(status_code=500, detail="System error")
        
        except Exception as e:
            logger.error(f"Ошибка с токеном: {e}")
            raise HTTPException(status_code=500, detail="System error")
    else:
        logger.error("Нет jwt токена для подтверждения кода")
        raise HTTPException(status_code=404, detail="Not found jwt code token")

    if rc.resend:
        send_code = True

    else:
        try:
            if not used:
                life_time_repeated_code = 1

                exp_token = token_info.get("exp")
                exp_repeated_code = curretly_msk() + timedelta(minutes=life_time_repeated_code)
                exp_repeated_code_iso = exp_repeated_code.isoformat()

                return_data = {
                    "verification_token": old_token,
                    "exp_repeated_code_iso": exp_repeated_code_iso,
                    "exp_token": exp_token,
                    "email": new_email,
                }
                token_info["used"] = True
                redis_data[rjp.name_key] = token_info
                __redis_save_jwt_token__.cached(redis_data)
            else:
                return_data = {
                    "email": new_email,
                    "verification_token": old_token,
                    }
                    
            send_code = False
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка с токеном: {e}")
            raise HTTPException(status_code=500, detail="System error")
    # если повторная отправка
    if send_code:
        ep = EmailProcess(new_email)
        try:
            return_data = ep.send_change_email(rjp, user_info.user_id, "confirm_code")

        except Exception as e:
            logger.error(f"Ошибка в функции send_change_email: {e}")
            raise HTTPException(status_code=500, detail="System error")
    
    return return_data

@router.post("/confirm_code", response_model=SuccessAnswer)
async def check_code(
    rc: SendCode, 
    user_info: UserProcess = Depends(template_not_found_user)
    ):
    verification_token = decode_jwt_token(rc.token)

    user_id = verification_token.get("user_id")
    if user_info.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

    code = verification_token.get("verification_code")
    success = False

    if code == int(rc.code):
        success = True

    return {
        "success": success,
    }

# password
@router.get("/confirm_password", response_class=HTMLResponse)
async def confirm_password():
    with open(path_html + "confirm_password.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(html_content)

@router.post("/confirm_password", response_model=SuccessMessageAnswer)
async def processing_password(
    sp: {},
    user_info: UserProcess = Depends(get_current_user_id),
): 
    data_token = decode_jwt_token(sp.token)

    user_id = data_token.get("user_id")
    if user_info.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")
    
    user = await user_info.get_user_info(w_pswd=True, w_email_hash=False)
    
    if user.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

    password_hash = PSWD_context.hash(sp.password)

    if user.get("password") != password_hash:
        return {
            "success": False,
            "message": "Invalid password"
        }
    else:
        return {
            "success": True,
            "message": "Confirm password"
            }
    


