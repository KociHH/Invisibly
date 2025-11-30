from fastapi import APIRouter, HTTPException, Body, status
import logging
from shared.config.variables import path_html, PSWD_context, curretly_msk
from app.crud.user import UserProcess
from app.schemas.code import SendCode, ConfirmPassword
from app.services.rabbitmq.client import EmailRpcClient
from app.services.jwt import decode_jwt_token, create_token
from datetime import timedelta
from app.db.redis.keys import RedisUserKeys
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)
router = APIRouter()

class ConfirmCodePack:
    def __init__(self):
        pass

    def validation_confirm_token(
        self,
        user_process: UserProcess,
        token_info: dict | None = None,
        ):
        if not token_info:
            user_keys = RedisUserKeys(user_process.user_id)
            token_info: dict = user_keys.jwt_confirm_token_obj.checkpoint_key.get_cached() or {}

        if token_info:
            try:
                old_token = token_info.get("token")
                if not old_token:
                    logger.error("Токен не найден в token_info")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
            
                used: bool = token_info.get("used", False)
                old_token_data = decode_jwt_token(old_token)
                user_id = old_token_data.get("user_id")
            
                if user_process.user_id != user_id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: you can only modify your own account")

                code = old_token_data.get("verification_code")
                new_email = old_token_data.get("new_email")
                if not code or not new_email:
                    logger.error(f'code либо new_email не найден из токена: {code} {new_email}')
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid data token")
        
                exp_token = token_info.get("exp_token")
                if not exp_token:
                    logger.error(f'exp_token не найден из токена: {exp_token}')
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid data token")
        
            except Exception as e:
                logger.error(f"Ошибка с токеном: {e}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server error")
        else:
            logger.error("Нет jwt токена для подтверждения кода")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found jwt code token")

        return {
            "used": used,
            "old_token_data": old_token_data,
            "old_token": old_token,
            "new_email": new_email,
            "code": code,
            "exp_token": exp_token
        }

class ConfirmCodeData(ConfirmCodePack):
    def __init__(self) -> None:
        super().__init__()
    
    async def route(
        self, 
        user_process: UserProcess,
        ) -> dict:

        user: dict = await _http_client.get_or_cache_user_info(user_process.user_id, ["email"], False)
        if user:
            email = user.get("email")

        if not email or not user:
            logger.error(f"Не найден email пользователя либо он сам {user_process.user_id}")
            raise HTTPException(status_code=500, detail="Server error")
        
        user_keys = RedisUserKeys(user_process.user_id)
        token_info: dict = user_keys.jwt_confirm_token_obj.checkpoint_key.get_cached() or {}
        
        validated_confirm_token = self.validation_confirm_token(user_process, token_info)
        used = validated_confirm_token.get("used")
        old_token = validated_confirm_token.get("old_token")
        new_email = validated_confirm_token.get("new_email")
        exp_token = validated_confirm_token.get('exp_token')

        return_data = {}
        try:
            if not used:
                life_time_repeated_code = 1

                exp_repeated_code = curretly_msk() + timedelta(minutes=life_time_repeated_code)
                exp_repeated_code_iso = exp_repeated_code.isoformat()

                return_data["verification_token"] = old_token,
                return_data["exp_repeated_code_iso"] = exp_repeated_code_iso,
                return_data["exp_token"] = exp_token,
                return_data["email"] = new_email,
                
                token_info["used"] = True
                user_keys.jwt_confirm_token_obj.checkpoint_key.cached(token_info)
            else:
                life_time_repeated_code = 1
                exp_repeated_code = curretly_msk() + timedelta(minutes=life_time_repeated_code)
                exp_repeated_code_iso = exp_repeated_code.isoformat()

                return_data["verification_token"] = old_token,
                return_data["exp_repeated_code_iso"] = exp_repeated_code_iso,
                return_data["exp_token"] = exp_token,
                return_data["email"] = new_email,
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка с токеном: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")
        return return_data
    
class ResendCode(ConfirmCodePack):
    def __init__(self):
        super().__init__()
    
    async def route(
        self,
        user_process: UserProcess
        ):
        user_keys = RedisUserKeys(user_process.user_id)
        token_info: dict = user_keys.jwt_confirm_token_obj.checkpoint_key.get_cached() or {}
        
        validated_confirm_token = self.validation_confirm_token(user_process, token_info)
        exp_token = validated_confirm_token.get('exp_token')
        
        if exp_token > curretly_msk().isoformat():
            logger.warning("Токен еще не истек для повторной отправки")
            raise HTTPException(status_code=status.HTTP_425_TOO_EARLY, detail="Token not expired")
        
        new_email = validated_confirm_token.get("new_email")
        
        try:
            ep = EmailRpcClient(new_email)
            return_data = await ep.send_change_email(user_process.user_id, user_process.user_id, "confirm_code")
        except Exception as e:
            logger.error(f"Ошибка в функции send_change_email: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")
    
        return return_data
        
    
class ConfirmCode:
    def __init__(self) -> None:
        pass
    
    async def route(
        self, 
        rc: SendCode,
        user_info: UserProcess
        ) -> dict:
        try:
            verification_token = decode_jwt_token(rc.token)

            user_id = verification_token.get("user_id")
            if user_info.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: you can only modify your own account")

            code = verification_token.get("verification_code")
            success = False

            if code == int(rc.code):
                success = True

            return {
                "success": success,
            }
        except Exception as e:
            logger.error(f"Ошибка в функции check_code: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")
        
class ConfirmPassword:
    def __init__(self) -> None:
        pass
    
    async def route(
        self, 
        sp: ConfirmPassword,
        user_info: UserProcess
        ) -> dict:
        data_token = decode_jwt_token(sp.token)

        user_id = data_token.get("user_id")
        if user_info.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: you can only modify your own account")
    
        user = await user_info.get_user_info(w_pswd=True, w_email_hash=False)
    
        if user.get("user_id") != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: you can only modify your own account")

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