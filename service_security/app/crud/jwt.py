from fastapi import HTTPException, status
from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.sql.tables import UserJWT
import logging

logger = logging.getLogger(__name__)

class UserJWTCrud:
    def __init__(self, db_session: AsyncSession, jti: str):
        self.db_session = db_session
        self.jti = jti
        self.user_jwt_dao = BaseDAO(UserJWT, self.db_session)
        
    async def find_jti(self):
        exists_jti = await self.user_jwt_dao.get_one(UserJWT.jti == self.jti)
        return exists_jti
    
    async def update_revoke(self, revoke: bool):
        update = await self.user_jwt_dao.update(
            UserJWT.jti == self.jti,
            {"revoke": revoke}
        )
        if not update:
            logger.error(f"Не обновились данные jti: {self.jti}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")
        
        return update