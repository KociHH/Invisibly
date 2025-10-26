from httpx import get
from app.db.sql.tables import UserJWT
from fastapi import APIRouter, HTTPException
import logging
from app.services.jwt import verify_refresh_token, create_token
from app.db.sql.settings import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.crud.user import CreateTable, UserProcess, RedisJsonsProcess
from kos_Htools.sql.sql_alchemy import BaseDAO
from jose import jwt, exceptions
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from app.schemas.token import DeleteTokenRedis, RefreshTokenRequest
from app.schemas.response_model import EventTokensResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/refresh", response_model=EventTokensResponse)
async def refresh_access_update(
    request_body: RefreshTokenRequest, 
    db_session: AsyncSession = Depends(get_db_session),
    user_info: UserProcess = Depends(require_existing_user_dep)
    ):
    """with SQL response"""
    try:
        verify = verify_refresh_token(request_body.refresh_token)
        if not verify:
            logger.error('Не вернулось значение функции verify_refresh_token')
            raise HTTPException(status_code=500, detail="Server error")

        user_id, jti = verify
        token_dao = BaseDAO(UserJWT, db_session)
        existing_token = await token_dao.get_one(UserJWT.jti == jti)

        if existing_token and existing_token.revoked:
            logger.warning(f"Повторное использование отозванного refresh token для user_id: {user_id}")
            raise HTTPException(status_code=401, detail="Refresh token has been revoked or is invalid")

        if existing_token:
            await token_dao.update(UserJWT.jti == jti, data={"revoked": True})
        else:
            raise HTTPException(status_code=401, detail="Refresh token not found in database")

        if user_info.user_id != user_id:
            logger.warning(f"Юзер из токена {user_id} != юзеру из бд {user_info.user_id}")
            raise HTTPException(status_code=404, detail="User does not match token user_id")

        new_access_token, _ = create_token(data={"user_id": user_id}, token_type="access")
        new_refresh_token, new_jti = create_token(data={"user_id": user_id}, token_type="refresh")

        if not any(new_access_token and new_refresh_token and new_jti):
            logger.error("Не вернулось значение (create_access_token, create_refresh_token)")
            raise HTTPException(status_code=500, detail="Server error")

        create_sql = CreateTable(db_session)
        await create_sql.create_UJWT(save_elements={
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
        raise HTTPException(status_code=401, detail="Refresh token expire")
    except exceptions.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        logger.error(f"Ошибка при обновлении токена: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@router.post("/access", response_model=EventTokensResponse)
async def access_update(request_body: RefreshTokenRequest):
    try:
        verify = verify_refresh_token(request_body.refresh_token)
        if not verify:
            logger.error('Не вернулось значение функции verify_refresh_token')
            raise HTTPException(status_code=500, detail="Server error")
    
        user_id, _ = verify
        access_token, _ = create_token(data={"user_id": user_id})

        if not access_token:
            logger.error("Не вернулось значение (create_access_token)")
            raise HTTPException(status_code=500, detail="Server error")
    
        return {
            "access_token": access_token, 
            "refresh_token": None,
            "token_type": "access",
            } 
    except HTTPException as e:
        raise e
    except exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expire")
    except exceptions.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        logger.error(f'Внезапная ошибка в функции access_update:\n {e}')
        raise HTTPException(status_code=500, detail="Server error") 

@router.post("/check_update_tokens")    
async def check_update_tokens(
    user_info: UserProcess = Depends(get_current_user_dep)
):
    try:
        return {
            "success": True,
            "user_id": user_info.user_id,
            "message": "Token is valid"
        }
    except Exception as e:
        logger.error(f"Не валидный токен либо дрегое: {e}")
        raise HTTPException(status_code=401, detail="Token validation failed")

@router.post("/redis/delete_token/user")
async def redis_delete_token_user(
    dtr: DeleteTokenRedis,
    user_info: UserProcess = Depends(require_existing_user_dep)
): 
    rjp = RedisJsonsProcess(user_info.user_id).constructor(dtr.domain)

    del_token = rjp.checkpoint_key.delete_key()
    if not del_token:
        logger.error(f"Функция delete_token завершилась с ошибкой: {del_token}")
        raise HTTPException(status_code=500, detail="Server error")
    
    else:
        return {
            "success": True,
            "message": "Deleted token!"
        }