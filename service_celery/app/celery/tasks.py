from datetime import timedelta
from service_celery.app.celery.app import celery_app
import asyncio
from db.sql.settings import get_db_session
import logging
from kos_Htools.sql.sql_alchemy import BaseDAO
from config.env import TOKEN_LIFETIME_DAYS
from app.services.user import CreateTable
from shared.data.redis.instance import __redis_save_sql_call__
from config.variables import curretly_msk

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
        
@celery_app.task
def cleaning_expiring_json():
    try:
        save_sql_call_data: dict | None = __redis_save_sql_call__.get_cached()
        if not save_sql_call_data:
            return
        
        keys_to_remove = []
        for user_key, value in save_sql_call_data.items():
            if not isinstance(value, dict) or 'exp' not in value:
                logger.warning(f"Некорректная структура данных для ключа {user_key}")
                continue
                
            if value['exp'] <= curretly_msk():
                keys_to_remove.append(user_key)
        
        if keys_to_remove:
            for key in keys_to_remove:
                save_sql_call_data.pop(key, None)
            
            __redis_save_sql_call__.cached(data=save_sql_call_data)
            logger.info(f"Удалено {len(keys_to_remove)} истекших записей")
        
        return save_sql_call_data
        
    except Exception as e:
        logger.error(f"Ошибка в функции cleaning_expiring_json:\n {e}")
        return None