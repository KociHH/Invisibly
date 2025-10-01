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
# не рабочий
class RedisJsonsProcess(RedisJsons):
    def __init__(self, user_id: int | str, handle: str) -> None:
        super().__init__(user_id, handle)

    async def get_or_cache_friends(
        self, 
        db_session: AsyncSession,
        sort_reverse: bool = False,
        ) -> dict:
        data: dict | None = __redis_save_friends__.get_cached()

        if not data:
            data = {}

        friends_data = data.get(self.name_key)
        if not friends_data:

            friends_dao = BaseDAO(FriendsUser, db_session)
            user_dao = BaseDAO(UserRegistered, db_session)

            friends = await friends_dao.get_all_column_values(
                (FriendsUser.friend_id, FriendsUser.addition_number),
                FriendsUser.user_id == self.user_id
            )

            if friends:
                friends.sort(lambda f: f[1], reverse=sort_reverse)
                
                for friend_pack in friends:
                    friend_id = friend_pack[0]
                    addition_number = friend_pack[1]

                    friends_info = await user_dao.get_one(
                        (UserRegistered.name, UserRegistered.surname),
                        UserRegistered.user_id == friend_id,
                    )

                    full_name = full_name_constructor(friends_info.name, friends_info.surname)

                    if self.name_key not in data:
                        data[self.name_key] = {}
                    data[self.name_key][friend_id] = {
                        "full_name": full_name,
                        "addition_number": addition_number
                    }

                __redis_save_friends__.cached(data)
            return data.get(self.name_key, {})
            
        else:
            return friends_data
