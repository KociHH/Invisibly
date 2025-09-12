from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from pydantic import BaseModel
from app.backend.jwt.token import verify_refresh_token, create_token
from app.backend.data.sql.tables import get_db_session, UserJWT
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.backend.utils.user import UserInfo
from app.backend.data.sql.utils import CreateSql
from kos_Htools.sql.sql_alchemy import BaseDAO
from config.env import REFRESH_TOKEN_LIFETIME_DAYS
from datetime import timedelta
from config.variables import curretly_msk
from jose import jwt, exceptions
from app.backend.utils.dependencies import template_not_found_user
from app.backend.data.pydantic import RefreshTokenRequest, SuccessAnswer, EventTokensResponse

sistem_err = "Server error"
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/refresh", response_model=EventTokensResponse)
async def refresh_access_update(
    request_body: RefreshTokenRequest, 
    db_session: AsyncSession = Depends(get_db_session),
    user_info: UserInfo = Depends(template_not_found_user)
    ):
    """with SQL response"""
    try:
        verify = verify_refresh_token(request_body.refresh_token)
        if not verify:
            logger.error('Не вернулось значение функции verify_refresh_token')
            raise HTTPException(status_code=500, detail=sistem_err)

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
            raise HTTPException(status_code=500, detail=sistem_err)

        issued_at = curretly_msk()
        expires_at = curretly_msk() + timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS)
        create_sql = CreateSql(db_session)
        await create_sql.create_UJWT(save_elements={
            "user_id": user_id,
            "jti": new_jti,
            "issued_at": issued_at,
            "expires_at": expires_at,
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
        raise HTTPException(status_code=500, detail=sistem_err)

@router.post("/access", response_model=EventTokensResponse)
async def access_update(request_body: RefreshTokenRequest):
    try:
        verify = verify_refresh_token(request_body.refresh_token)
        if not verify:
            logger.error('Не вернулось значение функции verify_refresh_token')
            raise HTTPException(status_code=500, detail=sistem_err)
    
        user_id, _ = verify
        access_token, _ = create_token(data={"user_id": user_id})

        if not access_token:
            logger.error("Не вернулось значение (create_access_token)")
            raise HTTPException(status_code=500, detail=sistem_err)
    
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
        raise HTTPException(status_code=500, detail=sistem_err) 

@router.post("/check_update_tokens")    
async def check_update_tokens(
    user_info: UserInfo = Depends(template_not_found_user)
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