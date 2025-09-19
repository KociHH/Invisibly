from fastapi import APIRouter, HTTPException, Body
from fastapi.params import Query
import logging
from app.backend.data.redis.utils import RedisJsons
from app.backend.data.sql.tables import UserRegistered, get_db_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.utils.user import EncryptEmail, PSWD_context, path_html, UserInfo
from app.backend.utils.dependencies import template_not_found_user
from app.backend.schemas.security import ChangeEmail, SendPassword, ResendCode, SendCode
from app.backend.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from config.variables import curretly_msk
from kos_Htools.sql.sql_alchemy.dao import BaseDAO


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/change/email", response_model=SuccessMessageAnswer)
async def change_email_post(
    change: ChangeEmail,
    db_session: AsyncSession = Depends(get_db_session),
    user_info: UserInfo = Depends(template_not_found_user)
):
    rj = RedisJsons(user_info.user_id, "change_email")
    user_dao = BaseDAO(UserRegistered, db_session)

    ee = EncryptEmail(change.new_email)
    email_hash = ee.hash_email()

    if not email_hash:
        logger.error(f"Email hash не был определен для пользователя {user_info.user_id} при смене почты.")
        raise HTTPException(status_code=500, detail="Server error: Email hash not defined.")
    
    email_update = await user_dao.update(
        UserRegistered.user_id == user_info.user_id,
        {
            "email": change.new_email,
            "email_hash": email_hash,
            })
    
    if not email_update:
        logger.error(f"По неизвестной причине email пользователя {user_info.user_id} не был обновлен")
        raise HTTPException(status_code=500, detail="Server error")
    
    data_result = rj.replace_items_data(items={
        "email": change.new_email,
        "email_hash": email_hash
    })
    if not data_result:
        logger.warning(f"Не удалось обновить кэш UserRegistered для пользователя {user_info.user_id}")
    
    delete_token = rj.delete_token()
    if not delete_token:
        logger.error(f"Функция {user_info.user_id} delete_token завершилась неудачно: {delete_token}")
        raise HTTPException(status_code=500, detail="Server error")

    logger.info(f"Email пользователя {user_info.user_id} успешно обновлен на {change.new_email}")
    return {
        "success": True, 
        "message": "Email updated"
        }

