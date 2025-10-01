from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.jwt import verify_token
from app.db.sql.settings import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import UserProcess
from app.services.http_client import _http_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user_id(
    token: str = Depends(oauth2_scheme), 
    db_session: AsyncSession = Depends(get_db_session)
    ):
    user_id = verify_token(token)
    user_info = UserProcess(user_id, db_session)
    return user_info.user_id

async def template_not_found_user(
    current_user_id: int = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_db_session)
    ):
    user_info = UserProcess(current_user_id, db_session)

    user_info._user_geted_data = await _http_client.get_user_info(user_info.user_id)

    if not user_info.check_user():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_info 