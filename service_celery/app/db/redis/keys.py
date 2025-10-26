import logging
from shared.crud.redis.create import RedisJsonsUser
from kos_Htools.redis_core import RedisBase
from redis import Redis

logger = logging.getLogger(__name__)

redis_client = Redis(host="redis")

class RedisUserKeys:
    def __init__(
        self, 
        user_id: str | int,           
        ):
        self.user_id = user_id
        self.service = "celery"
        
        self.chat_obj = self.constructor("chat", True)        
        self.friends_obj = self.constructor("friends", True) 
        self.user_obj = self.constructor("user", True)

    def constructor(self, domain: str, cache_call: bool = False):
        return RedisJsonsUser(self.user_id, domain, self.service, cache_call, redis_client)
