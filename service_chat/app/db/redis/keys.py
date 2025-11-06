import logging
from shared.crud.redis.create import RedisJsonsUser
from kos_Htools.redis_core import RedisShortened, RedisBase
from redis import Redis

logger = logging.getLogger(__name__)

redis_client = Redis(host="redis")

__redis_chat_conns_ws__ = RedisShortened("chat_conns_ws", [], redis_client)


class RedisUserKeys:
    def __init__(
        self, 
        user_id: str | int,         
        ):
        self.user_id = user_id
        self.service = "chat"

        self.cached_user_chats_obj = self.constructor("cached_user_chats_objs", True)

    def constructor(self, domain: str, cache_call: bool = False):
        return RedisJsonsUser(self.user_id, domain, self.service, cache_call, redis_client)


class RedisUserKeysChat:
    """
    Сохранение не под `user_id` ключей, а под `chat_id`
    """
    def __init__(
        self,
        chat_id: str | int,
        ):
        self.chat_id = chat_id
        self.service = "chat"
        
        self.chat_obj = self.constructor("chat", True)    
        self.message_obj = self.constructor("messages", True)
        
    def constructor(self, domain: str, cache_call: bool = False):
        return RedisJsonsUser(self.chat_id, domain, self.service, cache_call, redis_client)
