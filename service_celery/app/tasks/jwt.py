from datetime import timedelta
from app.celery.app import celery_app_jwt
import logging
from app.services.modules.jwt.service import JWTService

logger = logging.getLogger(__name__)

jwt_service = JWTService()

@celery_app_jwt.task
def check_jwt_token_date():
    return jwt_service.check_jwt_token_date.task()
        
@celery_app_jwt.task
def cleaning_expiring_keys_cache():
    return jwt_service.cleaning_expiring_keys_cache.task()