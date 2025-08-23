from datetime import timedelta
from app.backend.data.redis.instance import __redis_save_sql_call__, __redis_save_jwt_token__
from app.backend.utils.dependencies import curretly_msk
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

    def delete_all_data_user_item(self, item: str) -> dict:
        redis_data: dict = __redis_save_sql_call__.get_cached()
        if self.user_id not in redis_data:
            return {"data": "user not found"}
        
        remove_keys = []
        for key, data in redis_data.items():
            if self.user_id in key and isinstance(data, dict):
                item_data = data.get(item)
                if item_data:
                    remove_keys.append(key)

        for key in remove_keys:
            redis_data.pop(key)

        __redis_save_sql_call__.cached(data=redis_data)
        return {"data": "updated"}

class RedisJsons(GeneralInfo):
    def __init__(self, user_id: int | str, handle: str) -> None:
        self.handle = handle
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

        for keys, value in data.items():
            obj[keys] = value

        expiry_time = curretly_msk + timedelta(seconds=exp)
        obj["exp"] = expiry_time.isoformat()
        __redis_save_sql_call__.cached(data=redis_data, ex=None)
        return redis_data
    
    def save_jwt_token(self, token: str, exp: int) -> dict:
        """
        Можно сохранять либо обновлять в хранилище __redis_save_jwt_token__

        token: сам токен
        exp: время истечения *в минутах
        """

        redis_data: dict | None = __redis_save_jwt_token__.get_cached()
        obj = redis_data.get(self.name_key)
        data = {
            "token": token,
        }
        if not obj:
            redis_data[self.name_key] = {}

        expiry_time = curretly_msk + timedelta(minutes=exp)
        data["exp"] = expiry_time.isoformat()
        redis_data[self.name_key] = data

        __redis_save_jwt_token__.cached(data=redis_data, ex=None)
        return redis_data 

    async def get_or_cache_user_info(self, user_info: UserInfo, return_items: list | None = None):
        """
        Берет данные из __redis_save_sql_call__, если нет self.name_key в redis то береться из базы UserRegistered
        
        user_info: класс UserInfo объект юзера
        """
        if return_items == None:
            return_items = ["name", "surname", "login", "bio", "email"]

        obj: dict = redis_return_data(items=return_items, key_data=self.name_key)
        if obj.get("redis") == "empty":
            user = await user_info.get_user_info(w_pswd=False, w_email_hash=False)
            new_data = self.save_sql_call(
                {
                    "user_id": user.get("user_id"),
                    "name": user.get("name"),
                    "surname": user.get("surname"),
                    "login": user.get("login"),
                    "bio": user.get("bio"),
                    "email": user.get("email"),
                })
            if not new_data:
                logger.error("Не вернулось значение, либо ожидалось другое значение в функции save_sql_call")
                raise HTTPException(status_code=500, detail="Server error")

            obj = new_data
        return obj
