from datetime import timedelta
from typing import Any
from app.backend.data.redis.instance import __redis_save_sql_call__, __redis_save_jwt_token__
from config.variables import curretly_msk
import logging
from app.backend.utils.user import UserInfo
from fastapi import  HTTPException

logger = logging.getLogger(__name__)

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


class GeneralInfo:
    def __init__(self, user_id: int | str) -> None:
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

class RedisJsons(GeneralInfo):
    def __init__(self, user_id: int | str, handle: str) -> None:
        self.handle = handle
        self.user_id = user_id
        self.name_key = f"{self.user_id}-{self.handle}"
        super().__init__(user_id=user_id)

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
    
    def save_jwt_token(self, token: str, exp: int) -> dict:
        """
        Можно сохранять либо обновлять в хранилище __redis_save_jwt_token__

        token: сам токен
        exp: время истечения *в минутах
        """

        redis_data: dict | None = __redis_save_jwt_token__.get_cached()  
        if not redis_data:
            redis_data = {}

        data = {
            "token": token,
            "used": False
        }
        expiry_time = curretly_msk() + timedelta(minutes=exp)
        data["exp"] = expiry_time.isoformat()
        redis_data[self.name_key] = data

        __redis_save_jwt_token__.cached(data=redis_data, ex=None)
        return redis_data 

    async def get_or_cache_user_info(
        self, 
        user_info: UserInfo, 
        return_items: list | None = None,
        save_sql_redis: bool = True,
        ):
        """
        Берет данные из __redis_save_sql_call__, если нет self.name_key в redis то береться из базы UserRegistered
        
        user_info: класс UserInfo объект юзера
        """
        if return_items == None:
            return_items = ["name", "surname", "login", "bio", "email", "email_hash"]

        obj: dict = redis_return_data(items=return_items, key_data=self.name_key)

        if obj.get("redis") == "empty":
            user = await user_info.get_user_info(w_pswd=False, w_email_hash=False)
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

    def delete_token(self):
        try:
            jwt_tokens: dict | None = __redis_save_jwt_token__.get_cached()
            rj = RedisJsons(self.user_id, self.handle)

            if jwt_tokens:
                token_info: dict | None = jwt_tokens.get(rj.name_key)
                if token_info:
                    jwt_tokens.pop(rj.name_key)
                    __redis_save_jwt_token__.cached(jwt_tokens)
    
        except Exception as e:
            logger.error(f"Внезапная ошибка: {e}")
            return False
        return True