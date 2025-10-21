from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from app.schemas.data import FriendsRequestsInfo
from shared.crud.redis.create import RedisJsonsServerToken
from shared.crud.redis.dependencies import get_interservice_token_info
from shared.services.jwt.token import control_rules_interservice_token
from sqlalchemy.ext.asyncio import AsyncSession
from shared.config.variables import path_html, PSWD_context
from app.crud.user import UserProcess
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from app.db.sql.settings import get_db_session
from shared.services.jwt.exceptions import UNAUTHORIZED

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/friends_requests_info")
async def friends_requests_info_get(
    fri: FriendsRequestsInfo,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    try:
        write, delete, read = control_rules_interservice_token(token_info.payload, required_scopes=["read"])
    except Exception as e:
        logger.warning(f"Проверка межсервисного токена не удалась: {e}")
        raise UNAUTHORIZED
    
    if read:
        user_process = UserProcess(fri.user_id, db_session)
        
        consume = token_info.consume_interservice_token()
        if consume:
            return await user_process.friends_requests_info(fri.user_id, fri.get_fields)
        
        raise HTTPException(status_code=500, detail="Failed to consume token")
    raise HTTPException(status_code=403, detail="Not enough rights")