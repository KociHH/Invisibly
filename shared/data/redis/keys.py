from kos_Htools import BaseDAO
from shared.data.redis.variables import services_domains_access
from shared.services.tools.variables import names_services
from kos_Htools.redis_core import RedisBase, RedisDifKey
from redis import Redis
import logging

logger = logging.getLogger(__name__)

redis_client = Redis(host="redis")
redis_base_for_list = Redis(host="redis", decode_responses=True)

class RedisUserKeyDictConstructor:
    """
    Проверяет и создает название ключа в переменную `self.name_key`
        
    Инициализирует ключ под названием `self.name_key` в переменную `self.checkpoint_key`
        
    пример: `12345:profile` или с кешом запроса `12345:profile:cache`
    """
    def __init__(
        self, 
        user_id: str | int,
        domain: str, 
        service: str,
        cache_call: bool = False,
        _redis_client: Redis = redis_client
        ) -> None:
        """
        user_id: `id` пользователя, включен в создание ключа
        
        domain: название ключа, проверяется доступность на использование указанным `service`, включен в создание ключа
        
        service: имя сервиса откуда идет подключение, проверяет доступ к ключам и валидность сервиса
        
        cache_call: указывается тип ключа, если True, то `cache` добавляется к созданию ключа
        
        _redis_client: клиент `redis` для подключения к ключу
        """
        
        self._redis_client = _redis_client
        self.cache_call = cache_call
        self.user_id = user_id
        if isinstance(user_id, int):
            self.user_id = str(user_id)
        if service.upper() in names_services:
            self.service = service
        else:
            logger.error(f"Сервис {service} не найден")
            raise
        
        if self.check_domain(domain):
            self.domain = domain
            if cache_call:
                self.name_key = f"{self.user_id}:{self.domain}:cache"
            else:
                self.name_key = f"{self.user_id}:{self.domain}"
        else:
            logger.error(f"Домен {domain} сервиса {service} не найден")
            raise

        self.checkpoint_key = RedisBase(self.name_key, {}, self._redis_client)

    def create_check_sql_call_key(self) -> RedisBase | None:
        sql_call_cache = None
        if "cache" in self.name_key:
            sql_call_cache = RedisBase(self.name_key, {}, self._redis_client)
        return sql_call_cache

    def check_domain(self, domain: str) -> bool:
        domains: list = services_domains_access.get(self.service)
        if domain in domains:
            return True
        return False     

__redis_dif_key__ = RedisDifKey(redis_client)