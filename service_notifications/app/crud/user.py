from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from shared.crud.sql.user import UserCRUD
from app.db.redis.keys import RedisUserKeys
from shared.services.tools.other import full_name_constructor
from app.services.http_client import _http_client
from shared.config.variables import curretly_msk

class UserProcess(UserCRUD):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id=user_id, db_session=db_session)


class RedisJsonsProcess(RedisUserKeys):
    def __init__(self, user_id: int | str) -> None:
        super().__init__(user_id)

    def save_jwt_confirm_token(self, token: str, life_time_token: int):
        exp = curretly_msk() + timedelta(minutes=life_time_token)
        data = {
            "token": token,
            "user_id": self.user_id,
            "used": False,
            "exp": exp.isoformat()
        }
        self.jwt_confirm_token_obj.checkpoint_key.cached(data, life_time_token * 60)
        return data