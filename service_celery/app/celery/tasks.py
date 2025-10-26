from datetime import timedelta
from app.celery.app import celery_app
import asyncio
from db.sql.settings import get_db_session
import logging
from kos_Htools.sql.sql_alchemy import BaseDAO
from ...config import TOKEN_LIFETIME_DAYS
from app.crud.user import CreateTable
from app.db.redis.keys import RedisUserKeys, redis_client
from shared.config.variables import curretly_msk
from app.db.sql.tables import SecretKeyJWT

logger = logging.getLogger(__name__)

@celery_app.task
def check_jwt_token_date():
    async def _run_task():
        async for db_session in get_db_session():
            cs = CreateTable(db_session)
            skj = BaseDAO(SecretKeyJWT, db_session)
            key_obj = await skj.get_all()

            if key_obj:
                created = key_obj.created_key
                change = key_obj.change_key

                if created and change:
                    if (change - created) >= timedelta(days=TOKEN_LIFETIME_DAYS):
                        logger.info('Время жизни SECRET_KEY истекло, создаю новый.')
                        create_success = await cs.create_SKJ(db_session)
                        if create_success:
                            logger.info('Создался новый SECRET_KEY')
                        else:
                            logger.warning('Не удалось создать новый SECRET_KEY')
                    else:
                        logger.info('SECRET_KEY еще действителен.')
            else:
                logger.info('SECRET_KEY не найден, создаю новый.')
                create_success = await cs.create_SKJ(db_session)
                if create_success:
                    logger.info('Создался новый SECRET_KEY при инициализации.')
                else:
                    logger.error(f'Ошибка в функции create_SKJ: не удалось создать SECRET_KEY при инициализации.')
    
    asyncio.run(_run_task())
    return
        
@celery_app.task
def cleaning_expiring_keys_cache():
    try:
        keys = redis_client.keys()
        if keys:
            keys_cache = [k for k in keys if "cache" in k]
            
            if keys_cache:
                for key_cache_name in keys_cache:
                    key_cache_params = key_cache_name.split(":")
                    key_obj = RedisUserKeys(key_cache_params[0]).constructor(key_cache_params[1], True)
                    
                    key_data: dict = key_obj.checkpoint_key.get_cached() or {}
                    if not key_data:
                        return

                    now = curretly_msk()
                    keys_to_delete = False

                    for value in list(key_data.values()):
                        if not isinstance(value, dict) or 'exp' not in value:
                            logger.warning(f"Некорректная структура данных для ключа {key_obj.name_key}")
                            continue

                        exp = value['exp']
                        try:
                            if isinstance(exp, (int, float)):
                                expired = exp <= int(now.timestamp())
                            else:
                                expired = exp <= now
                        except Exception as e:
                            logger.warning(f"Не удалось сравнить exp для {key_obj.name_key}: {e}")
                            continue

                        if expired:
                            keys_to_delete = True

                    if keys_to_delete:
                        key_obj.checkpoint_key.delete_key()
                        logger.info(f"Удален ключ {key_obj.name_key} так как он истек")
        return

    except Exception as e:
        logger.exception(f"Ошибка в функции cleaning_expiring_json: {e}")
        return None