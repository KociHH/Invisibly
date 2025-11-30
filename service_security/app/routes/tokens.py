from fastapi import APIRouter
import logging
from app.db.sql.settings import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.crud.user import UserProcess
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from app.schemas.token import DeleteTokenRedis, RefreshTokenRequest
from app.schemas.response_model import EventTokensResponse
from app.services.modules.tokens.service import TokensService

router = APIRouter()
logger = logging.getLogger(__name__)

tokens_service = TokensService()

@router.post("/refresh", response_model=EventTokensResponse)
async def refresh_access_update(
    request_body: RefreshTokenRequest, 
    db_session: AsyncSession = Depends(get_db_session),
    user_process: UserProcess = Depends(require_existing_user_dep)
    ):
    return await tokens_service.refresh_access_update.route(request_body, db_session, user_process)

@router.post("/access", response_model=EventTokensResponse)
async def access_update(request_body: RefreshTokenRequest):
    return await tokens_service.access_update.route(request_body)

@router.post("/check_update_tokens")    
async def check_update_tokens(user_process: UserProcess = Depends(get_current_user_dep)):
    return await tokens_service.check_update_tokens.route(user_process)

@router.post("/redis/delete_token/user")
async def redis_delete_token_user(
    dtr: DeleteTokenRedis,
    user_process: UserProcess = Depends(require_existing_user_dep)
): 
    return await tokens_service.redis_delete_token_user.route(dtr, user_process)