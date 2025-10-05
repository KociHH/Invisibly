from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from shared.crud.sql.user import UserCRUD
from shared.data.redis.instance import __redis_save_friends__
from shared.crud.redis.create import RedisJsons
from shared.services.tools.other import full_name_constructor
from app.services.http_client import _http_client

class UserProcess(UserCRUD):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id=user_id, db_session=db_session)


class RedisJsonsProcess(RedisJsons):
    def __init__(self, user_id: int | str, handle: str) -> None:
        super().__init__(user_id, handle)

