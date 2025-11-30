from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.sql.tables import SecretKeyJWT

class SecretKeyJWTCrud:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.secret_key_jwt_dao = BaseDAO(SecretKeyJWT, self.db_session)
        
    async def get_all_secret_keys(self):
        get_all = await self.secret_key_jwt_dao.get_all()
        return get_all