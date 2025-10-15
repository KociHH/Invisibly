from fastapi import APIRouter, HTTPException, Body
from fastapi.params import Query
import logging
from app.db.sql.settings import get_db_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import EncryptEmailProcess, UserProcess, RedisJsonsProcess
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from app.schemas.change import ChangeEmail, SendPassword
from app.schemas.system import SendEmail
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from shared.config.variables import curretly_msk
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from app.services.http_client import _http_client


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/change/email", response_model=SuccessMessageAnswer)
async def change_email_post(
    change: ChangeEmail,
    user_info: UserProcess = Depends(require_existing_user_dep)
):
    rjp = RedisJsonsProcess(user_info.user_id, "change_email")

    ee = EncryptEmailProcess(change.new_email)
    email_hash = ee.hash_email()

    if not email_hash:
        logger.error(f"Email hash не был определен для пользователя {user_info.user_id} при смене почты.")
        raise HTTPException(status_code=500, detail="Server error: Email hash not defined.")
    
    email_update = await _http_client.update_user({
        "email": change.new_email,
        "email_hash": email_hash,
    }) 
    
    if not email_update:
        logger.error(f"По неизвестной причине email пользователя {user_info.user_id} не был обновлен")
        raise HTTPException(status_code=500, detail="Server error")
    
    data_result = rjp.replace_items_data(items={
        "email": change.new_email,
        "email_hash": email_hash
    })
    if not data_result:
        logger.warning(f"Не удалось обновить кэш UserRegistered для пользователя {user_info.user_id}")
    
    delete_token = rjp.delete_token()
    if not delete_token:
        logger.error(f"Функция {user_info.user_id} delete_token завершилась неудачно: {delete_token}")
        raise HTTPException(status_code=500, detail="Server error")

    logger.info(f"Email пользователя {user_info.user_id} успешно обновлен на {change.new_email}")
    return {
        "success": True, 
        "message": "Email updated"
        }

@router.post("/send/email", response_model=SendEmail)
async def send_email():
    pass

