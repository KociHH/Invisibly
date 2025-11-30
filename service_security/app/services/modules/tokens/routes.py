from fastapi import APIRouter, HTTPException, status
import logging
from app.services.jwt import verify_refresh_token, create_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import UserProcess, RedisJsonsProcess
from app.crud.create import CreateCrud
from jose import jwt, exceptions
from app.schemas.token import DeleteTokenRedis, RefreshTokenRequest
from app.crud.jwt import UserJWTCrud

logger = logging.getLogger(__name__)

class RefreshAccessUpdate:
    def __init__(self) -> None:
        pass
    
    async def route(
        self, 
        request_body: RefreshTokenRequest, 
        db_session: AsyncSession, 
        user_process: UserProcess
        ) -> dict:
        try:
            verify = verify_refresh_token(request_body.refresh_token)
            if not verify:
                logger.error('Не вернулось значение функции verify_refresh_token')
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")

            user_id, jti = verify
            user_jwt_crud = UserJWTCrud(db_session, jti)
            existing_token = await user_jwt_crud.find_jti()

            if existing_token and existing_token.revoked:
                logger.warning(f"Повторное использование отозванного refresh token для user_id: {user_id}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has been revoked or is invalid")

            if existing_token:
                await user_jwt_crud.update_revoke(True)
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found in database")

            if user_process.user_id != user_id:
                logger.warning(f"Юзер из токена {user_id} != юзеру из бд {user_process.user_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not match token user_id")

            new_access_token, _ = create_token(data={"user_id": user_id}, token_type="access")
            new_refresh_token, new_jti = create_token(data={"user_id": user_id}, token_type="refresh")

            if not any(new_access_token and new_refresh_token and new_jti):
                logger.error("Не вернулось значение (create_access_token, create_refresh_token)")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")

            create_crud = CreateCrud(db_session)
            await create_crud.create_UJWT(save_elements={
                "user_id": user_id,
                "jti": new_jti,
                "token_type": "refresh",
            })

            return {
                "access_token": new_access_token, 
                "refresh_token": new_refresh_token, 
                "token_type": "bearer"
                }
        except HTTPException as e:
            raise e
        except exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expire")
        except exceptions.JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        except Exception as e:
            logger.error(f"Ошибка при обновлении токена: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")
        
class AccessUpdate:
    def __init__(self) -> None:
        pass
    
    async def route(
        self, 
        request_body: RefreshTokenRequest,
        ) -> dict:
        try:
            verify = verify_refresh_token(request_body.refresh_token)
            if not verify:
                logger.error('Не вернулось значение функции verify_refresh_token')
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")
    
            user_id, _ = verify
            access_token, _ = create_token(data={"user_id": user_id})

            if not access_token:
                logger.error("Не вернулось значение (create_access_token)")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")
    
            return {
                "access_token": access_token, 
                "refresh_token": None,
                "token_type": "access",
            } 
        except HTTPException as e:
            raise e
        except exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expire")
        except exceptions.JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        except Exception as e:
            logger.error(f'Внезапная ошибка в функции access_update:\n {e}')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error") 
        
class CheckUpdateTokens:
    def __init__(self) -> None:
        pass
    
    async def route(
        self, 
        user_process: UserProcess
        ) -> dict:
        try:
            return {
                "success": True,
                "user_id": user_process.user_id,
                "message": "Token is valid"
            }
        except Exception as e:
            logger.error(f"Не валидный токен либо другая ошибка: {e}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token validation failed")
        
class RedisDeleteTokenUser:
    def __init__(self) -> None:
        pass
    
    async def route(
        self, 
        dtr: DeleteTokenRedis,
        user_process: UserProcess
        ) -> dict:
        domain_map = {
            "change_email": "jwt_confirm_token",
            "confirm_code": "jwt_confirm_token",
        }
        domain = domain_map.get(dtr.domain, dtr.domain)

        rjp = RedisJsonsProcess(user_process.user_id).constructor(domain)

        rjp.checkpoint_key.delete_key()
    
        return {
            "success": True,
            "message": "Deleted token!"
        }