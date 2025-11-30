from datetime import datetime
from fastapi import HTTPException, status
from kos_Htools import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.sql.tables import FrozenAccounts
from shared.config.variables import curretly_msk
import logging

logger = logging.getLogger(__name__)

class CreateCrud:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def create_frozen_accounts(
        self,
        user_id: str | int,
        delete_at: datetime,
        frozen_at: datetime | None = None,
    ):
        frozen_dao = BaseDAO(FrozenAccounts, self.db_session)
        
        if not frozen_at:
            frozen_at = curretly_msk()
        
        create = await frozen_dao.create({
            "user_id": user_id,
            "frozen_at": frozen_at,
            "delete_at": delete_at
        })   
        if not create:
            logger.error(f"Юзер {user_id} не был создан в FrozenAccounts")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")
        
        return create