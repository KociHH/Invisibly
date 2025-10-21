from typing import Callable, Awaitable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from shared.services.jwt.token import verify_token_user
from sqlalchemy.ext.asyncio import AsyncSession
from shared.crud.sql.user import UserCRUD
from shared.services.http_client.service_free import ServiceFreeHttpClient
from shared.services.http_client.variables import get_http_client_state

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(get_db_session):
    async def _dep(
        token: str = Depends(oauth2_scheme),
        db_session: AsyncSession = Depends(get_db_session),
    ):
        user_id = verify_token_user(token)
        return UserCRUD(user_id, db_session)
    return _dep

def require_existing_user(get_db_session, get_http_client):
    async def _dep(
        _http_client: ServiceFreeHttpClient = Depends(get_http_client),
        user_process: UserCRUD = Depends(get_current_user(get_db_session)),
    ):
        if not await user_process.check_user_existence(_http_client):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user_process
    return _dep
