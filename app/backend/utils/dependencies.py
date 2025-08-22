from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.backend.jwt.token import verify_token
from app.backend.data.sql.tables import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.utils.user import UserInfo
from kos_Htools.utils.time import DateTemplate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
curretly_msk = DateTemplate().conclusion_date(option="time_now").replace(tzinfo=None)

async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    user_id = verify_token(token)
    return user_id

async def template_not_found_user(
        current_user_id: int = Depends(get_current_user_id),
        db_session: AsyncSession = Depends(get_db_session)
        ):
    user_info = UserInfo(current_user_id, db_session)
    if not user_info.check_user():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return user_info 