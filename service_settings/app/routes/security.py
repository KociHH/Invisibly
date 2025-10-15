from datetime import timedelta
from operator import ge
from typing import Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Query
from fastapi.responses import HTMLResponse
import logging

from httpx import get
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep, oauth2_scheme
from fastapi import Depends
from jose import jwt
from shared.data.redis.instance import __redis_save_sql_call__, __redis_save_jwt_token__
from app.schemas.account import DeleteAccount
from app.schemas.change import ChangePassword
from app.schemas.change import ChangeEmailForm
from app.schemas.response_model import EmailSendVerify
from shared.schemas.response_model import SuccessMessageAnswer, SuccessAnswer
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.services.rabbitmq.client import EmailRpcClient
from app.crud.user import EncryptEmailProcess, UserProcess, RedisJsonsProcess
from shared.config.variables import curretly_msk, path_html, PSWD_context
from app.services.http_client import _http_client
from app.db.sql.tables import FrozenAccounts

logger = logging.getLogger(__name__)
router = APIRouter()

# email
@router.get("/change_email/data")
async def change_email_data(
    user_info: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    user_id = user_info.user_id

    rjp = RedisJsonsProcess(user_id, "change_email")

    del_token = rjp.delete_token()
    if not del_token:
        logger.error("Функция delete_token завершилась с ошибкой")
        raise HTTPException(status_code=500, detail="Server error")

    obj: dict = await _http_client.get_or_cache_user_info(user_id, "UserRegistered", token)
    
    email = obj.get("email")
    ee = EncryptEmailProcess(email)
    email = ee.email_part_encrypt()

    return {"email": email}

@router.post("/change_email", response_model=EmailSendVerify)
async def processing_email(
    cef: ChangeEmailForm, 
    user_info: UserProcess = Depends(get_current_user_dep)
):
    current_user_id = user_info.user_id

    if cef.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")
    
    handle_cause = "change_email"

    rjp = RedisJsonsProcess(current_user_id, handle_cause)
    ee = EncryptEmailProcess(user_info.db_session)

    tokens: dict | None = __redis_save_jwt_token__.get_cached()
    token_info = tokens.get(rjp.name_key) if tokens else False

    db_email_hash, _ = await ee.email_verification(user_info.db_session, current_user_id)
    if db_email_hash:
        return {
            "success": False, 
            "message": "This email is busy",
        }

    if token_info:
        del_token = rjp.delete_token()
        if not del_token:
            logger.error("Функция delete_token завершилась с ошибкой")
            raise HTTPException(status_code=500, detail="Server error")

    ep = EmailRpcClient(cef.email)
    try:
        result = ep.send_change_email(current_user_id, handle_cause, current_user_id, handle_cause)
        return result
            
    except Exception as e:
        logger.error(f"Ошибка в функции send_change_email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")       
    
# password
@router.post("/change_password", response_class=SuccessMessageAnswer)
async def processing_password(
    np: ChangePassword,
    user_info: UserProcess = Depends(get_current_user_dep),
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
            password_update = await _http_client.update_user({
                "password": entered_password
            })
            
            if not password_update:
                logger.error(f"По неизвестной причине password пользователя {current_user_id} не был обновлен")
                raise HTTPException(status_code=500, detail="Server error")

            return {
                "success": True,
                "message": "Password updated"
            }
        
# delete account
@router.get("/delete_account")
async def delete_account():
    return {"message": "Browser request handler for get"}
 
@router.post("/delete_account", response_model=SuccessMessageAnswer)
async def processing_delete(
    da: DeleteAccount,
    user_info: UserProcess = Depends(require_existing_user_dep),
):
    current_user_id = user_info.user_id

    if da.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied: you can only modify your own account")
    
    if da.delete_confirmation:
        userb = BaseDAO(FrozenAccounts, user_info.db_session)

        frozen_time = 7
        frozen_at = curretly_msk()
        delete_at = curretly_msk() + timedelta(days=frozen_time)

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