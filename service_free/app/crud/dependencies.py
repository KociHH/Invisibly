from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from shared.services.jwt.token import verify_token_user
from app.db.sql.settings import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import UserProcess
from app.services.http_client import _http_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user_id(
    token: str = Depends(oauth2_scheme), 
    db_session: AsyncSession = Depends(get_db_session)
    ):
    user_id = verify_token_user(token)
    user_process = UserProcess(user_id, db_session)
    return user_process

async def require_existing_user(
    user_process: UserProcess = Depends(get_current_user_id),
    ):
    if not user_process.get_user_info(False, False):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_process 