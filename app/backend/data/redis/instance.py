from kos_Htools.redis_core.redisetup import RedisShortened
from redis import Redis
import logging

logger = logging.getLogger(__name__)

redis_base = Redis()
redis_base_for_list = Redis(decode_responses=True)

redis_save_sql_call = 'save_sql_call'
redis_save_jwt_token = 'save_jwt_token'

__redis_save_sql_call__ = RedisShortened(key=redis_save_sql_call, data={}, redis_client=redis_base)
__redis_save_jwt_token__ = RedisShortened(key=redis_save_jwt_token, data={}, redis_client=redis_base)