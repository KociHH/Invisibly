from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from shared.crud.sql.user import UserCRUD
from shared.crud.redis.create import RedisJsons
import logging
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)

class UserProcess(UserCRUD):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id=user_id, db_session=db_session)

class RedisJsonsProcess(RedisJsons):
    def __init__(self, user_id: int | str, handle: str) -> None:
        super().__init__(user_id, handle)

    async def get_or_cache_user_info(
        self, 
        user_process: UserProcess, 
        return_items: list | None = None,
        save_sql_redis: bool = True,
        ):
        """
        Берет данные из __redis_save_sql_call__, если нет self.name_key в redis то береться из базы UserRegistered
        
        UserProcess: класс UserProcess объект юзера
        """
        if return_items == None:
            return_items = ["name", "surname", "login", "bio", "email", "email_hash"]

        obj: dict = self.redis_return_data(items=return_items, key_data=self.name_key)

        if obj.get("redis") == "empty":
            user = await user_process.get_user_info(w_pswd=False, w_email_hash=False)
            if user is None:
                logger.error(f"Не удалось получить информацию о пользователе {self.user_id} из базы данных.")
                raise HTTPException(status_code=500, detail="Server error: User not found in database.")
            
            new_data = {
                "user_id": user.get("user_id"),
                "name": user.get("name"),
                "surname": user.get("surname"),
                "login": user.get("login"),
                "bio": user.get("bio"),
                "email": user.get("email"),
            }

            if save_sql_redis:
                new_data = self.save_sql_call(new_data)
                if not new_data:
                    logger.error("Не вернулось значение, либо ожидалось другое значение в функции save_sql_call")
                    raise HTTPException(status_code=500, detail="Server error")

            obj = new_data
        return obj