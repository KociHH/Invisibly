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
        self.service = "notifications"
             
        self.friends_obj = self.constructor("friends", True)
        self.jwt_confirm_token_obj = self.constructor("jwt_confirm_token")

    def constructor(self, domain: str, cache_call: bool = False):
        return RedisJsonsUser(self.user_id, domain, self.service, cache_call, redis_client)
