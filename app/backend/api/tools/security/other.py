import datetime
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
import logging
import uuid
from fastapi import Depends
from app.backend.utils.user import PSWD_context, path_html, UserInfo
from app.backend.utils.dependencies import template_not_found_user
from app.backend.data.pydantic import SendPassword, SuccessAnswer, ResendСode, SendCode
from app.backend.utils.other import send_code_email
from app.backend.jwt.token import create_token
from app.backend.jwt.utils import decode_jwt_token
from datetime import timedelta
from app.backend.data.redis.utils import RedisJsons
from app.backend.data.redis.instance import __redis_save_jwt_token__
from app.backend.utils.dependencies import curretly_msk

logger = logging.getLogger(__name__)
router = APIRouter()

# email code
@router.get("/confirm_code", response_class=HTMLResponse)
# 1. /confirm_code?cause=... 2. /confirm_code?cause=...&resend=...?
async def confirm_code(
    rc: ResendСode = Depends(),
    cause: str = Query(..., description="Причина вызова confirm_code"),
    user_info: UserInfo = Depends(template_not_found_user),
    ):
    with open(path_html + "confirm_code.html", "r", encoding="utf-8") as html_file:
        html_content = html_file.read()
    
    life_time_token = 5
    life_time_repeated_code = 1
    send_code = False

    user = await user_info.get_user_info(w_pswd=False, w_email_hash=False)
    if user:
        email = user.get("email")

    if not email or not user:
        logger.error(f"Не найден email пользователя либо он сам {user_info.user_id}")
        raise HTTPException(status_code=500, detail="Server error")
    
    rj = RedisJsons(user_info.user_id, cause)
    redis_data: dict | None = __redis_save_jwt_token__.get_cached()
    old_token = redis_data.get(rj.name_key)

    if rc.resend:
        send_code = True

    elif old_token:
        try:
            old_verification_token = decode_jwt_token(old_token)
            user_id = old_verification_token.get("user_id")
            
            if user_info.user_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

            code = old_verification_token.get("verification_code")
            if not code:
                logger.error(f'Код не найден из токена: {code}')
                raise HTTPException(status_code=500, detail="System error")

            send_code = False
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка с токеном: {e}")
            raise HTTPException(status_code=500, detail="System error")
    
    else:
        send_code = True

    if send_code:
        result = send_code_email(email, "для смены пароля.", 6)
    
        if result:
            success = result.get("success")

            if success:
                code: int = result.get("code")
                token_data = {
                    "user_id": user_info.user_id,
                    "verification_code": code,
                    "jti": str(uuid.uuid4()),
                }
                verification_token, _ = create_token(
                    token_data, 
                    timedelta(minutes=life_time_token)
                    )
                redis_data = rj.save_jwt_token(verification_token, life_time_token)

                if not redis_data:
                    logger.error(f'Не полученна дата *redis_data при сохранении в redis: {redis_data}')
                    raise HTTPException(status_code=500, detail="Date not received")
                
                # Подсчет дат
                data_token = redis_data.get(rj.name_key)
                exp_token = data_token.get("exp")

                exp_repeated_code = curretly_msk + timedelta(minutes=life_time_repeated_code)
                exp_repeated_code_iso = exp_repeated_code.isoformat()

            else:
                error = result.get("error")
                raise HTTPException(status_code=500, detail=error)
        else:
            raise HTTPException(status_code=500, detail="The code was not delivered")

    html_content = html_content.replace("{{verification_token}}", verification_token)
    html_content = html_content.replace("{{email}}", email)

    html_content = html_content.replace("{{exp_token}}", exp_token)
    html_content = html_content.replace("{{exp_repeated_code}}", exp_repeated_code_iso)

    html_content = html_content.replace("{{life_time_token}}", life_time_token)
    html_content = html_content.replace("{{life_time}}", life_time_repeated_code)

    return HTMLResponse(content=html_content)

@router.post("/confirm_code", response_model=SuccessAnswer)
async def check_code(
    rc: SendCode = Depends(), 
    user_info: UserInfo = Depends(template_not_found_user)
    ):
    verification_token = decode_jwt_token(rc.token)

    user_id = verification_token.get("user_id")
    if user_info.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

    code = verification_token.get("verification_code")
    success = False

    if code == rc.code:
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

@router.post("/confirm_password", response_model=SuccessAnswer)
async def processing_password(
    sp: SendPassword,
    user_info: UserInfo = Depends(template_not_found_user),
): 
    data_token = decode_jwt_token(sp.token)

    user_id = data_token.get("user_id")
    if user_info.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")
    
    user = await user_info.get_user_info(w_pswd=True, w_email_hash=False)
    if not user:
        raise HTTPException(status_code=500, detail="Server error")
    
    if user.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

    password_hash = PSWD_context.hash(sp.password)

    if user.get("password") != password_hash:
        return {
            "success": False,
            "message": "Invalid password"
        }
    else:
        return {"success": True}
    


