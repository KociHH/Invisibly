from typing import Callable, Awaitable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from shared.services.jwt.token import verify_token_user
from sqlalchemy.ext.asyncio import AsyncSession
from shared.crud.sql.user import UserCrudShared
from shared.services.http_client.service_free import ServiceFreeHttpClient
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(get_db_session):
    async def _dep(
        token: str = Depends(oauth2_scheme),
        db_session: AsyncSession = Depends(get_db_session),
    ):
        user_id = verify_token_user(token)
        return UserCrudShared(user_id, db_session)
    return _dep

def require_existing_user(get_db_session, get_http_client):
    async def _dep(
        _http_client: ServiceFreeHttpClient = Depends(get_http_client),
        user_process: UserCrudShared = Depends(get_current_user(get_db_session)),
    ):
        user_existence = await user_process.check_user_existence(_http_client)
        if not user_existence:
            logger.error(f"Пользователь {user_process.user_id} не найден")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user_process
    return _dep
