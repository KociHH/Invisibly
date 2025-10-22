from kos_Htools.redis_core import RedisBase, RedisDifKey
from redis import Redis
import logging

logger = logging.getLogger(__name__)

redis_base = Redis(host="redis")
redis_base_for_list = Redis(host="redis", decode_responses=True)

redis_save_sql_call = 'save_sql_call'
redis_save_jwt_code_token = 'save_code_token'
redis_save_friends = "save_friends"
redis_save_chats = "save_chats"
redis_save_jwt_interservice_token = "save_interservice_token"

__redis_save_sql_call__ = RedisBase(key=redis_save_sql_call, data={}, redis_client=redis_base)
__redis_save_jwt_code_token__ = RedisBase(key=redis_save_jwt_code_token, data={}, redis_client=redis_base)
__redis_save_friends__ = RedisBase(key=redis_save_friends, data={}, redis_client=redis_base)
__redis_save_chats__ = RedisBase(key=redis_save_chats, data={}, redis_client=redis_base)

__redis_dif_key__ = RedisDifKey(redis_base)