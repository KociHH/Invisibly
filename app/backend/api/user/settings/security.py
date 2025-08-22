from datetime import timedelta
from typing import Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from app.backend.jwt.utils import decode_jwt_token
from app.backend.utils.user import PSWD_context, path_html, UserInfo
from fastapi import Depends
from app.backend.utils.dependencies import  template_not_found_user
from jose import jwt
from app.backend.data.redis.instance import __redis_save_sql_call__
from app.backend.data.redis.utils import RedisJsons
from app.backend.data.pydantic import ConfirmCode, DeleteAccount, NewPassword, SuccessMessageAnswer, UserEditProfileNew, NewEmail
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.backend.data.sql.tables import FrozenAccounts, UserRegistered
from app.backend.utils.other import send_code_email
from app.backend.utils.user import path_html, DBUtils, EncryptEmail
from app.backend.utils.dependencies import get_current_user_id, get_db_session
from app.backend.utils.dependencies import curretly_msk

logger = logging.getLogger(__name__)
router = APIRouter()

# email
@router.get("/change_email", response_class=HTMLResponse)
async def change_email(user_info: UserInfo = Depends(template_not_found_user)):
    with open(path_html + "user/security/change_email.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    user = await user_info.get_user_info(w_pswd=False, w_email_hash=False)
    email = None
    if user:
        email = user.get("email")

    if not email or not user:
        logger.info(f"Не найден email пользователя либо он сам {user_info.user_id}")
        raise HTTPException(status_code=500, detail="Server error")

    ee = EncryptEmail(email)
    email = ee.email_part_encrypt()

    html_content = html_content.replace("{{email}}", email)

    return HTMLResponse(content=html_content)

@router.post("/change_email", response_model=SuccessMessageAnswer)
async def processing_email(
    ne: NewEmail, 
    user_info: UserInfo = Depends(template_not_found_user)
):
    current_user_id = user_info.user_id

    if ne.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")
    
    userb = BaseDAO(UserRegistered, user_info.db_session)
    dbu = DBUtils(user_info.db_session)

    if not ne.confirm:
        db_email_hash, email_hash = await dbu.email_verification(ne.email, current_user_id)
        if db_email_hash:
            return {
                "success": False, 
                "message": "This email is busy"
            }
    
    if ne.confirm and ne.confirm != "true":
        result_send = send_code_email(ne.email, "для подтверждения почты.")
        if result_send:
            success = result_send.get("seccess")
            error = result_send.get("error")

            if success:
                return {
                    "send_for_verification": True
                }
            else:
                logger.error(f"Произошла ошибка при отправке кода на почту {ne.email}: {error}")
                raise HTTPException(status_code=500, detail=error)
        else:
            raise HTTPException(status_code=500, detail="The code was not delivered")

    email_update = await userb.update(
        UserRegistered.user_id == current_user_id,
        {
            "email": ne.email,
            "email_hash": email_hash,
            })
    
    if not email_update:
        logger.error(f"По неизвестной причине email пользователя {current_user_id} не был обновлен")
        raise HTTPException(status_code=500, detail="Server error")
    
    rj = RedisJsons(current_user_id, "change_email")
    data_result = rj.delete_all_data_user_item(item="email")
    if not data_result:
        logger.warning(f"Не вернулось значение dict функции delete_all_data_user_item: {data_result}")
    
    logger.info(f"Email пользователя {current_user_id} успешно обновлен на {ne.email}")
    return {
        "success": True, 
        "message": "Email updated"
        }        
    
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
        frozen_at = curretly_msk
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