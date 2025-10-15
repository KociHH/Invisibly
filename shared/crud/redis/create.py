from datetime import timedelta
from typing import Any
from shared.data.redis.instance import __redis_save_sql_call__, __redis_save_jwt_token__
from shared.config.variables import curretly_msk
import logging
from shared.crud.sql.user import UserCRUD
from fastapi import  HTTPException

logger = logging.getLogger(__name__)

class RedisJsons:
    def __init__(self, user_id: int | str, handle: str) -> None:
        self.handle = handle
        self.user_id = user_id
        self.name_key = f"{self.user_id}-{self.handle}"
        if isinstance(user_id, int):
            self.user_id = str(user_id)
        self.user_id = user_id

    def replace_items_data(self, items: dict[str, Any]) -> dict:
        """
        Заменяет данные ключей где встречается self.user_id на новые в redis
        Использует __redis_save_sql_call__
        """

        redis_data: dict = __redis_save_sql_call__.get_cached()
        
        user_data_found = False

        for key_in_redis, user_specific_data in redis_data.items():
            if str(self.user_id) in key_in_redis and isinstance(user_specific_data, dict):
                user_data_found = True
                for key_items, new_value in items.items():
                    if key_items in user_specific_data:
                        user_specific_data[key_items] = new_value
        
        if not user_data_found:
            return {"data": "user not found in cache"}

        __redis_save_sql_call__.cached(data=redis_data)
        return {"data": "updated"}

    def save_sql_call(self, data: dict, exp: int = 300) -> dict:
        """
        Можно сохранять либо обновлять в хранилище __redis_save_sql_call__

        data: дата для сохранения
        exp: время истечения *в секундах
        """

        redis_data: dict | None = __redis_save_sql_call__.get_cached()
        obj = redis_data.get(self.name_key)
        if not obj:
            redis_data[self.name_key] = {}
            obj = redis_data.get(self.name_key)

        for keys, value in data.items():
            obj[keys] = value

        expiry_time = curretly_msk() + timedelta(seconds=exp)
        obj["exp"] = expiry_time.isoformat()
        __redis_save_sql_call__.cached(data=redis_data, ex=None)
        return data

    @staticmethod
    def redis_return_data(
        items: list[str],
        key_data: str,
        ) -> dict:
        """
        Использует __redis_save_sql_call__

        items: [id, name, ...]
        key_data: user_id-edit_profile и тд
        """
        base_data: dict | None = __redis_save_sql_call__.get_cached()
        if not key_data in base_data.keys() or not base_data:
            return {"redis": "empty"}

        new_data = {}
        for i in items:
            new_data[i] = base_data[key_data].get(i)
        return new_data

    def delete_token(self):
        try:
            jwt_tokens: dict | None = __redis_save_jwt_token__.get_cached()

            if jwt_tokens:
                token_info: dict | None = jwt_tokens.get(self.name_key)
                if token_info:
                    jwt_tokens.pop(self.name_key)
                    __redis_save_jwt_token__.cached(jwt_tokens)
    
        except Exception as e:
            logger.error(f"Внезапная ошибка: {e}")
            return False
        return True