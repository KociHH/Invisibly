from datetime import timedelta
from email.policy import HTTP
from typing import Any
from redis import Redis
from shared.data.redis.keys import redis_client, __redis_dif_key__
from shared.config.variables import curretly_msk
import logging
from fastapi import HTTPException
from kos_Htools.redis_core import RedisBase
from shared.services.tools.other import l
from shared.data.redis.keys import RedisUserKeyDictConstructor

logger = logging.getLogger(__name__)

INTERSERVICE_TOKEN_LIFETIME_MINUTES = int(l("INTERSERVICE_TOKEN_LIFETIME_MINUTES"))

class RedisJsonsUser(RedisUserKeyDictConstructor):
    def __init__(
        self, 
        user_id: int | str, 
        domain: str,
        service: str,
        cache_call: bool = False,
        _redis_client: Redis = redis_client
        ) -> None:
        super().__init__(user_id, domain, service, cache_call, _redis_client)
        
        self.sql_call_key = self.create_check_sql_call_key(self)
        
    def replace_items_data(self, items: dict[str, Any]) -> dict:
        """
        Заменяет данные ключей где встречается параметр `cache` в ключах
        
        items: Параметры которые надо обновить
        
        return: Возвращает `{"data": "updated"}`, если имя ключа не имеет тип `cache`, то `{error: "not valid type cache in name_key"}`
        если не найдены данные ключа, то `{"error": "user data not found in cache"}`
        """
        if not self.sql_call_key:
            return {"error": "not valid type cache in name_key"}

        redis_data: dict = self.sql_call_key.get_cached() or {}
        
        user_data_found = False

        if redis_data:
            for key, old_value in redis_data.items():
                for key_items, new_value in items.items():
                    if key_items in key and old_value != new_value:
                        key[key_items] = new_value
        
        if not user_data_found:
            return {"error": "user data not found in cache"}

        self.sql_call_key.cached(data=redis_data)
        return {"error": "updated"}

    def save_sql_call(self, data: dict, exp: int = 300) -> dict:
        """
        data: дата для сохранения
        exp: время истечения *в секундах
        
        return: Возвращает данные ключа, либо при ошибке `{"error": "not valid type cache in name_key"}`
        """
        if not self.sql_call_key:
            return {"error": "not valid type cache in name_key"}

        redis_data: dict = self.sql_call_key.get_cached() or {}
        obj = redis_data.get(self.name_key)
        if not obj:
            redis_data[self.name_key] = {}
            obj = redis_data.get(self.name_key)

        for keys, value in data.items():
            obj[keys] = value

        expiry_time = curretly_msk() + timedelta(seconds=exp)
        obj["exp"] = expiry_time.isoformat()
        self.sql_call_key.cached(data=redis_data, ex=None)
        print(data)
        return data

    def redis_return_data(
        self,
        items: list[str],
        ) -> dict:
        """
        items: [id, name, ...]
        key_data: user_id-edit_profile и тд
        
        return: Возвращает словарь запрашиваемых данных, либо при ошибке `{"redis": "empty"}`
        """
        base_data: dict = self.sql_call_key.get_cached() or {}
        if not base_data:
            return {"redis": "empty"}

        new_data = {}
        for i in items:
            new_data[i] = base_data.get(i)
        return new_data
    
    
class RedisJsonsServerToken:
    def __init__(
        self,
        jti: str,
    ) -> None:
        self.jti = jti
        self.payload: dict | None = None
        self.__redis_save_jwt_interservice_token__ = RedisBase(self.jti, {}, redis_client=__redis_dif_key__.redis)
        
    def save_interservice_token(
        self, 
        token: str, 
        ) -> dict:
        """
        Сохраняет как `per-to-key` и проверяет на существование токена
        """
        redis_data: dict = self.__redis_save_jwt_interservice_token__.get_cached() or {}
        if not redis_data:
            result_data = {
                "token": token,
            }
            self.__redis_save_jwt_interservice_token__.cached(result_data, ex=INTERSERVICE_TOKEN_LIFETIME_MINUTES * 60)
            return result_data
        return {}
    
    def get_interservice_token(self) -> dict | None:
        """
        Получает конкретный ключ по своим атрибутам
        """
        redis_data: dict = self.__redis_save_jwt_interservice_token__.get_cached() or {}
        return redis_data if redis_data else None
    
    def delete_interservice_token(self) -> bool:
        """
        Удаляет ключ. В системе не используется, только в админке
        """
        try:
            redis_data: dict = self.__redis_save_jwt_interservice_token__.get_cached()

            if redis_data:
                self.__redis_save_jwt_interservice_token__.delete_key()
            return True
        
        except Exception as e:
            logger.error(f"Внезапная ошибка: {e}")
            return False
    
    def consume_interservice_token(self, _redis_client: Redis | None = None) -> bool:
        """ 
        Удаляет и возвращает сам ключ, в других ситуациях False 
        """
        try:
            if _redis_client:
                __redis_dif_key__.redis = _redis_client
            result = __redis_dif_key__.__redis_consume_key__(self.jti)
            return result
        except Exception as e:
            logger.error(f"Ошибка при потреблении межсервисного токена {self.jti}: {e}")
            return False