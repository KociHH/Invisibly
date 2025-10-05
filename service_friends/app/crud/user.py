from typing import Any
from kos_Htools.sql.sql_alchemy.dao import BaseDAO
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from shared.crud.redis.create import RedisJsons
from shared.data.redis.instance import __redis_save_friends__
from app.db.sql.tables import FriendsUser, SendFriendRequests
from shared.services.tools.other import full_name_constructor
import logging
from shared.crud.sql.user import UserCRUD
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)

class UserProcess(UserCRUD):
    def __init__(self, user_id: int, db_session: AsyncSession) -> None:
        super().__init__(user_id=user_id, db_session=db_session)
        self.friend_user = BaseDAO(FriendsUser, db_session)
        self.send_friend_request = BaseDAO(SendFriendRequests, db_session)
        self._cached_user_info = None

    async def find_friend_by_param(
        self, 
        param_name: str, 
        param_value: str | Any
        ) -> dict:
        attr = {
            "user_id": FriendsUser.user_id, 
            "friend_id": FriendsUser.friend_id, 
            "addition_number": FriendsUser.addition_number, 
            }
        if param_name not in attr:
            logger.error(f"Не найден данный параметр: {param_name}")
            return {'error': f"Param {param_name} not found"}
        
        column_to_search = attr[param_name]

        user_dao = BaseDAO(FriendsUser, self.db_session)

        user_info = await user_dao.get_one(column_to_search == param_value)
        if user_info:
            return {
                "user_id": user_info.user_id,
                "friend_id": user_info.friend_id,
                "addition_number": user_info.addition_number,
            }
        return {}

    async def update_friend(self, update_data: dict) -> bool:
        if not update_data: # {}
            return False

        friend_dao = BaseDAO(FriendsUser, self.db_session)
        
        try:
            success = await friend_dao.update(
                FriendsUser.user_id == self.user_id, 
                **update_data
                )
            return success
        except Exception as e:
            logger.error(f"Ошибка при обновлении пользователя {self.user_id}: {e}")
            return False

    async def get_friend_info(
        self, 
        friend_id: int | str,
        user_id: int | str | None = None
        ) -> dict[str, Any] | None:
        try:
            if not friend_id:
                if not self.check_user():
                    return None
            
                user_obj = self._cached_user_info
                if not user_obj:
                    user_obj = await self._user_geted_data 
                    self._cached_user_info = user_obj
            else:
                user_obj = await self.friend_user.get_one(
                    and_(FriendsUser.friend_id == friend_id, FriendsUser.user_id == user_id or self.user_id))

            info = {
                "user_id": user_obj.user_id,
                "friend_id": user_obj.friend_id,
                "addition_number": user_obj.addition_number,
            }

            return info
            
        except Exception as e:
            logger.error(f'Ошибка в get_user_info:\n{e}')
            return None

    async def friends_requests_info(
        self, 
        user_id: int | str, 
        fields: list[str] | None
        ):
        available_fields = {
            "user_id": SendFriendRequests.user_id,
            "request_user_id": SendFriendRequests.request_user_id,
            "send_at": SendFriendRequests.send_at
        }
        
        friends_dao = BaseDAO(SendFriendRequests, self.db_session)
        
        if fields:
            invalid_fields = [f for f in fields if f not in available_fields]
            if invalid_fields:
                raise ValueError(f"Invalid fields: {invalid_fields}")
            
            columns = [available_fields[field] for field in fields]
        else:
            columns = list(available_fields.values())

        friends_requests = await friends_dao.get_all_column_values(
            columns,
            SendFriendRequests.user_id == user_id,
        )

        return friends_requests


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

            friends = await friends_dao.get_all_column_values(
                (FriendsUser.friend_id, FriendsUser.addition_number),
                FriendsUser.user_id == self.user_id
            )

            if friends:
                friends.sort(key=lambda f: f[1], reverse=sort_reverse)
                
                for friend_pack in friends:
                    friend_id = friend_pack[0]
                    addition_number = friend_pack[1]

                    friends_info = await _http_client.get_user_info(friend_id)
                    
                    full_name = full_name_constructor(friends_info.get("name"), friends_info.get("surname"))

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
