from fastapi import APIRouter, Depends, HTTPException, Request, status
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from shared.crud.redis.create import RedisJsonsServerToken
from shared.services.jwt.token import control_rules_interservice_token
from app.crud.create import CreateCrud
from app.schemas.export import CreateUJWT
from shared.services.jwt.exceptions import UNAUTHORIZED

logger = logging.getLogger(__name__)

class CreateUserJWTPost:
    def __init__(self) -> None:
        pass
    
    async def route(
        self, cujwt: CreateUJWT, 
        token_info: RedisJsonsServerToken, 
        db_session: AsyncSession,
        ) -> dict:
        try:
            write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["write"])
        except Exception as e:
            logger.warning(f"Проверка межсервисного токена не удалась: {e}")
            raise UNAUTHORIZED
    
        if write:
            create_crud = CreateCrud(db_session)
    
            consume = token_info.consume_interservice_token()
            if consume:
                return await create_crud.create_UJWT({
                "user_id": cujwt.user_id,
                "jti": cujwt.jti,
                "token_type": cujwt.token_type,
                "issued_at": cujwt.issued_at,
                "expires_at": cujwt.expires_at,
            })
            
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to consume token")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights")