from fastapi import APIRouter, Depends, HTTPException, Request
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from shared.crud.redis.create import RedisJsonsServerToken
from shared.crud.redis.dependencies import get_interservice_token_info
from shared.services.jwt.token import control_rules_interservice_token
from app.crud.user import CreateTable, UserProcess
from app.db.sql.settings import get_db_session
from app.schemas.data import CreateUJWT
from shared.services.jwt.exceptions import UNAUTHORIZED
from shared.config.variables import curretly_msk

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create_UJWT")
async def create_UJWT_post(
    cujwt: CreateUJWT,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    try:
        write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["write"])
    except Exception as e:
        logger.warning(f"Проверка межсервисного токена не удалась: {e}")
        raise UNAUTHORIZED
    
    if write:
        create_tab = CreateTable(db_session)
    
        consume = token_info.consume_interservice_token()
        if consume:
            return await create_tab.create_UJWT({
            "user_id": cujwt.user_id,
            "jti": cujwt.jti,
            "token_type": cujwt.token_type,
            "issued_at": cujwt.issued_at,
            "expires_at": cujwt.expires_at,
        })
            
        raise HTTPException(status_code=500, detail="Failed to consume token")
    raise HTTPException(status_code=403, detail="Not enough rights")