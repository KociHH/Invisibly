from datetime import timedelta
from typing import Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Query
from fastapi.responses import HTMLResponse
import logging
from app.backend.jwt.utils import decode_jwt_token
from app.backend.utils.user import PSWD_context, path_html, UserInfo
from fastapi import Depends
from app.backend.utils.dependencies import  template_not_found_user
from jose import jwt
from app.backend.data.redis.instance import __redis_save_sql_call__, __redis_save_jwt_token__
from app.backend.data.redis.utils import RedisJsons
from app.backend.schemas.security import DeleteAccount, NewPassword, ChangeEmailForm
from app.backend.schemas.response_model import SuccessAnswer, EmailSendVerify, SuccessMessageAnswer
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.backend.data.sql.tables import FrozenAccounts, UserRegistered
from app.backend.utils.other import EmailProcess
from app.backend.utils.user import path_html, DBUtils, EncryptEmail
from app.backend.utils.dependencies import get_current_user_id, get_db_session
from config.variables import curretly_msk
from app.backend.jwt.token import create_token
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

# email
@router.get("/change_email", response_class=HTMLResponse)
async def change_email():
    with open(path_html + "user/security/change_email.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    html_content = html_content.replace("{{email}}", "")

    return HTMLResponse(content=html_content)

@router.get("/change_email/data")
async def change_email_data(
    user_info: UserInfo = Depends(template_not_found_user)
    ):
    user_id = user_info.user_id

    rj = RedisJsons(user_id, "change_email")

    del_token = rj.delete_token()
    if not del_token:
        logger.error("Функция delete_token завершилась с ошибкой")
        raise HTTPException(status_code=500, detail="Server error")

    rj = RedisJsons(user_id, "UserRegistered")
    obj: dict = await rj.get_or_cache_user_info(user_info)
    
    email = obj.get("email")
    ee = EncryptEmail(email)
    email = ee.email_part_encrypt()

    return {"email": email}

@router.post("/change_email", response_model=EmailSendVerify)
async def processing_email(
    cef: ChangeEmailForm, 
    user_info: UserInfo = Depends(template_not_found_user)
):
    current_user_id = user_info.user_id

    if cef.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")
    
    rj = RedisJsons(current_user_id, "change_email")
    dbu = DBUtils(user_info.db_session)

    tokens: dict | None = __redis_save_jwt_token__.get_cached()
    token_info = tokens.get(rj.name_key) if tokens else False

    db_email_hash, _ = await dbu.email_verification(cef.email, current_user_id)
    if db_email_hash:
        return {
            "success": False, 
            "message": "This email is busy",
        }

    if token_info:
        del_token = rj.delete_token()
        if not del_token:
            logger.error("Функция delete_token завершилась с ошибкой")
            raise HTTPException(status_code=500, detail="Server error")

    ep = EmailProcess(cef.email)
    try:
        result = ep.send_change_email(rj, current_user_id, "change_email")
        return result
            
    except Exception as e:
        logger.error(f"Ошибка в функции send_change_email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")       
    
# password
@router.get("/change_password", response_class=HTMLResponse)
async def change_password():
    with open(path_html + "user/security/change_password.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    return html_content

@router.post("/change_password", response_class=SuccessMessageAnswer)
async def processing_password(
    np: NewPassword,
    user_info: UserInfo = Depends(template_not_found_user),
):
    current_user_id = user_info.user_id

    if np.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")

    if not np.confirm:
        return {
            "send_for_verification": True
        }
    else:
        user = await user_info.get_user_info(w_pswd=True, w_email_hash=False)
        if not user:
            raise HTTPException(status_code=500, detail="Server error")
        
        password = user.password
        entered_password = PSWD_context.hash(np.password)

        if password == entered_password:
            return {
                "success": False,
                "message": "The new password should not be the same as the old password."
            }
        else:
            userb = BaseDAO(UserRegistered, user_info.db_session)

            password_update = userb.update(
                UserRegistered.user_id == current_user_id, 
                {
                    "password": entered_password,
                    })
            
            if not password_update:
                logger.error(f"По неизвестной причине password пользователя {current_user_id} не был обновлен")
                raise HTTPException(status_code=500, detail="Server error")

            return {
                "success": True,
                "message": "Password updated"
            }
        
# delete account
@router.get("/delete_account", response_class=HTMLResponse)
async def delete_account():
    with open(path_html + "user/security/delete_account.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    return HTMLResponse(html_content)
 
@router.post("/delete_account", response_model=SuccessMessageAnswer)
async def processing_delete(
    da: DeleteAccount,
    user_info: UserInfo = Depends(template_not_found_user),
):
    current_user_id = user_info.user_id

    if da.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")
    
    if da.delete_confirmation:
        userb = BaseDAO(FrozenAccounts, user_info.db_session)

        frozen_time = 7
        frozen_at = curretly_msk()
        delete_at = frozen_at + timedelta(days=frozen_time)

        add_frozen = userb.create({
            "user_id": da.user_id,
            "frozen_at": frozen_at,
            "delete_at": delete_at,
        })

        if not add_frozen:
            logger.error(f"По неизвестной причине пользователь {current_user_id} не был добавлен в базу FrozenAccounts")
            raise HTTPException(status_code=500, detail="Server error")
        
        logger.info(f"Юзер {current_user_id} добавлен в базу FrozenAccounts")
        return {
            "success": True,
            "message": "User added"
            }
    return {
        "success": False,
        "message": "User not added; delete_confirmation = False"
        }