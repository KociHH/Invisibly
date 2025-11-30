from datetime import timedelta
from operator import ge
from typing import Any
from fastapi import APIRouter, HTTPException, Request, status
import logging
from app.schemas.account import DeleteAccount
from app.schemas.change import ChangePassword
from app.schemas.change import ChangeEmailForm
from app.crud.create import CreateCrud
from app.services.rabbitmq.client import EmailRpcClient
from app.crud.user import EncryptEmailProcess, UserProcess, RedisJsonsProcess
from shared.config.variables import curretly_msk, PSWD_context
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)

class ChangeEmailData:
    def __init__(self):
        pass
    
    async def route(
        self,
        user_process: UserProcess
    ):
        user_id = user_process.user_id

        obj: dict = await _http_client.get_or_cache_user_info(user_id)
    
        rjp = RedisJsonsProcess(user_process.user_id)
        token_info: dict = rjp.jwt_confirm_token_obj.checkpoint_key.get_cached() or {}

        if token_info:
            rjp.jwt_confirm_token_obj.checkpoint_key.delete_key()
        
        email = obj.get("email")
        ee = EncryptEmailProcess(email)
        email = ee.email_part_encrypt()

        return {"email": email}
    
class ProcessingEmail:
    def __init__(self):
        pass
    
    async def route(
        self,
        cef: ChangeEmailForm, 
        user_process: UserProcess,
    ):
        current_user_id = user_process.user_id

        if cef.user_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: you can only modify your own account")

        ee = EncryptEmailProcess(cef.email)

        db_email_hash, _ = await ee.email_verification(current_user_id)
        if db_email_hash:
            return {
                "success": False, 
                "message": "This email is busy",
            }

        ep = EmailRpcClient(cef.email)
        try:
            result = await ep.send_change_email(current_user_id, current_user_id, "change_email")
            logger.info(f"Результат отправки email: {result}")
        
            if result.get("success") is False:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Ошибка отправки email: {error_msg}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to send verification email: {error_msg}")
        
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка в функции send_change_email: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to send verification email")       
    
class ProcessingDelete:
    def __init__(self):
        pass
    
    async def route(
        self,
        da: DeleteAccount,
        user_process: UserProcess,
    ):
        current_user_id = user_process.user_id

        if da.user_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: you can only modify your own account")
    
        if da.delete_confirmation:
            create_crud = CreateCrud(user_process.db_session)

            frozen_time = 7
            frozen_at = curretly_msk()
            delete_at = curretly_msk() + timedelta(days=frozen_time)

            add_frozen = create_crud.create(
                user_id = da.user_id,
                frozen_at = frozen_at,
                delete_at = delete_at,
            )

            if not add_frozen:
                logger.error(f"По неизвестной причине пользователь {current_user_id} не был добавлен в базу FrozenAccounts")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")
        
            logger.info(f"Юзер {current_user_id} добавлен в базу FrozenAccounts")
            return {
                "success": True,
                "message": "User added"
            }
        return {
            "success": False,
            "message": "User not added; delete_confirmation = False"
        }
        
class ProcessingPassword:
    def __init__(self):
        pass
    
    async def route(
        self,
        np: ChangePassword,
        user_process: UserProcess
    ):
        current_user_id = user_process.user_id

        if np.user_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: you can only modify your own account")

        if not np.confirm:
            return {
                "send_for_verification": True
            }
        else:
            user = await user_process.get_user_info(w_pswd=True, w_email_hash=False)
            if not user:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")
        
            password = user.password
            entered_password = PSWD_context.hash(np.password)

            if password == entered_password:
                return {
                    "success": False,
                    "message": "The new password should not be the same as the old password."
                }
            else:
                password_update = await _http_client.update_user(
                    {
                        "password": entered_password
                    },
                    current_user_id
                    )
            
                if not password_update:
                    logger.error(f"По неизвестной причине password пользователя {current_user_id} не был обновлен")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")

                return {
                    "success": True,
                    "message": "Password updated"
                }