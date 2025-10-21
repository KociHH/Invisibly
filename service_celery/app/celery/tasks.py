from datetime import timedelta
from app.celery.app import celery_app
import asyncio
from db.sql.settings import get_db_session
import logging
from kos_Htools.sql.sql_alchemy import BaseDAO
from ...config import TOKEN_LIFETIME_DAYS
from app.services.user import CreateTable
from shared.data.redis.instance import __redis_save_sql_call__
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
        
@celery_app.task
def cleaning_expiring_json():
    try:
        redis_data: dict | None = __redis_save_sql_call__.get_cached() or {}
        if not redis_data:
            return

        now = curretly_msk()
        keys_to_remove: list[str] = []

        for key, value in list(redis_data.items()):
            if not isinstance(value, dict) or 'exp' not in value:
                logger.warning(f"Некорректная структура данных для ключа {key}")
                continue

            exp = value['exp']
            try:
                if isinstance(exp, (int, float)):
                    expired = exp <= int(now.timestamp())
                else:
                    expired = exp <= now
            except Exception as e:
                logger.warning(f"Не удалось сравнить exp для {key}: {e}")
                continue

            if expired:
                keys_to_remove.append(key)

        if keys_to_remove:
            for k in keys_to_remove:
                redis_data.pop(k, None)
            __redis_save_sql_call__.cached(data=redis_data)
            logger.info(f"Удалено {len(keys_to_remove)} истекших записей")

        return redis_data

    except Exception as e:
        logger.exception(f"Ошибка в функции cleaning_expiring_json: {e}")
        return None