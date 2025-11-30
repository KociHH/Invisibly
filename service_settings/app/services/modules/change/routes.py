from fastapi import APIRouter, HTTPException, Body, status
import logging
from fastapi import Depends
from app.crud.user import EncryptEmailProcess, UserProcess, RedisJsonsProcess
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from app.schemas.change import ChangeEmail as cheme_ChangeEmail
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)

class ChangeEmail:
    def __init__(self):
        pass
    
    async def route(
        self,
        change: cheme_ChangeEmail,
        user_process: UserProcess = Depends(require_existing_user_dep)
    ):
        rjp = RedisJsonsProcess(user_process.user_id)

        ee = EncryptEmailProcess(change.new_email)
        email_hash = ee.hash_email()

        if not email_hash:
            logger.error(f"Email hash не был определен для пользователя {user_process.user_id} при смене почты.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Server error: Email hash not defined.")
    
        email_update = await _http_client.update_user(
            {
                "email": change.new_email,
                "email_hash": email_hash,
            }, 
            user_process.user_id
            ) 
    
        if not email_update:
            logger.error(f"По неизвестной причине email пользователя {user_process.user_id} не был обновлен")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")
    
        data_result = rjp.user_obj.replace_items_data(items={
            "email": change.new_email,
            "email_hash": email_hash
        })
        error = data_result.get("error")
        if error:
            logger.warning(f"Не удалось обновить кэш ключа {rjp.user_obj.name_key} для пользователя {user_process.user_id}: {error}")
    
        rjp.jwt_confirm_token_obj.checkpoint_key.delete_key()

        logger.info(f"Email пользователя {user_process.user_id} успешно обновлен на {change.new_email}")
        return {
            "success": True, 
            "message": "Email updated"
        }