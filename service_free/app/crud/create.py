from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.db.sql.tables import UserRegistered
from datetime import datetime
import logging
from shared.config.variables import curretly_msk

logger = logging.getLogger(__name__)

class CreateCrud:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session
    
    async def create_user(
        self,
        password: str,
        login: str,
        name: str,
        email: str,
        email_hash: str,
        surname: str | None = None,
        ):
        user_dao = BaseDAO(UserRegistered, self.db_session)
        
        registration_date = curretly_msk()
        
        create = await user_dao.create({
            "password": password,
            "login": login,
            "name": name,
            "surname": surname,
            "email": email,
            "email_hash": email_hash,
            "registration_date": registration_date,
        })
        if not create:
            logger.error(f"Юзер не был создан")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not created")
        return create