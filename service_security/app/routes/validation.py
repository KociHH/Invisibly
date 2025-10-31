import re
from fastapi import APIRouter, HTTPException, Body
from fastapi.params import Query
from fastapi.responses import HTMLResponse
import logging
import uuid
from fastapi import Depends
from httpx import get
from shared.config.variables import path_html, PSWD_context, curretly_msk
from app.crud.user import UserProcess
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep, oauth2_scheme
from app.schemas.code import ResendCode, SendCode
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from app.services.rabbitmq.client import EmailRpcClient
from app.services.jwt import decode_jwt_token, create_token
from datetime import timedelta
from app.crud.user import RedisJsonsProcess
from app.db.redis.keys import RedisUserKeys
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)
router = APIRouter()

# email code
@router.get("/confirm_code/data")
# 1. /confirm_code?cause=... 2. /confirm_code?cause=...&resend=...?
async def confirm_code_data(
    rc: ResendCode = Depends(),
    cause: str = Query(..., description="Причина вызова confirm_code"),
    user_info: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    
    send_code = False

    user: dict = await _http_client.get_or_cache_user_info(user_info.user_id, ["email"], False)
    if user:
        email = user.get("email")

    if not email or not user:
        logger.error(f"Не найден email пользователя либо он сам {user_info.user_id}")
        raise HTTPException(status_code=500, detail="Server error")
    
    user_keys = RedisUserKeys(user_info.user_id)
    token_info: dict = user_keys.jwt_confirm_token_obj.checkpoint_key.get_cached() or {}
    new_email: str | None = None

    if token_info:
        try:
            old_token = token_info.get("token")
            if not old_token:
                logger.error("Токен не найден в token_info")
                raise HTTPException(status_code=404, detail="Token not found")
            
            used: bool = token_info.get("used", False)
            old_verification_token = decode_jwt_token(old_token)
            user_id = old_verification_token.get("user_id")
            
            if user_info.user_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

            code = old_verification_token.get("verification_code")
            new_email = old_verification_token.get("new_email")
            if not code or not new_email:
                logger.error(f'code либо new_email не найден из токена: {code} {new_email}')
                raise HTTPException(status_code=500, detail="Server error")
        
        except Exception as e:
            logger.error(f"Ошибка с токеном: {e}")
            raise HTTPException(status_code=500, detail="Server error")
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
                user_keys.jwt_confirm_token_obj.checkpoint_key.cached(token_info)
            else:
                life_time_repeated_code = 1
                exp_token = token_info.get("exp")
                exp_repeated_code = curretly_msk() + timedelta(minutes=life_time_repeated_code)
                exp_repeated_code_iso = exp_repeated_code.isoformat()

                return_data = {
                    "email": new_email,
                    "verification_token": old_token,
                    "exp_repeated_code_iso": exp_repeated_code_iso,
                    "exp_token": exp_token,
                }
                    
            send_code = False
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка с токеном: {e}")
            raise HTTPException(status_code=500, detail="Server error")
    # повторная отправка
    if send_code:
        ep = EmailRpcClient(new_email)
        try:
            return_data = await ep.send_change_email(user_info.user_id, user_info.user_id, "confirm_code")

        except Exception as e:
            logger.error(f"Ошибка в функции send_change_email: {e}")
            raise HTTPException(status_code=500, detail="Server error")
    
    return return_data

@router.post("/confirm_code", response_model=SuccessAnswer)
async def check_code(
    rc: SendCode, 
    user_info: UserProcess = Depends(require_existing_user_dep)
    ):
    try:
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
    except Exception as e:
        logger.error(f"Ошибка в функции check_code: {e}")
        raise HTTPException(status_code=500, detail="Server error")    

# password not working
@router.post("/confirm_password", response_model=SuccessMessageAnswer)
async def processing_password(
    sp: dict,
    user_info: UserProcess = Depends(get_current_user_dep),
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
    


