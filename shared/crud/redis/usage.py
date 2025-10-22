from email.policy import HTTP
from http import server
from typing import Any
from shared.crud.redis.create import RedisJsonsServerToken
from shared.services.jwt.exceptions import UNAUTHORIZED
from shared.services.jwt.token import create_disposable_interservice_token, SECRET_KEY, ALGORITHM
from shared.config.variables import curretly_msk
from jose import jwt, exceptions
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def create_add_interservice_token(data: dict) -> str:
    """
    Создает через метод `create_disposable_interservice_token` и сохраняет токен через метод `save_interservice_token`
    
    Пример необходимых параметров data: 
    {
        "iss": "SERVICE_A",
        "aud": "SERVICE_B",
        "scopes": ["read", "write"]
    }
    """
    token, jti = create_disposable_interservice_token(data=data)
    redis_instance = RedisJsonsServerToken(jti)
    result = redis_instance.save_interservice_token(
        token=token,
        )
    if not result:
        raise HTTPException(status_code=403, detail="This token is already in use")
    return token

def verify_interservice_token(token: str) -> dict[str, Any]:
    """
    Проверяет межсервисный токен через `InterserviceTokenManager`
    """
    from shared.services.jwt.token import InterserviceTokenManager
    from shared.crud.redis.create import RedisJsonsServerToken
    
    manager = InterserviceTokenManager(redis_token_class=RedisJsonsServerToken)
    return manager.verify_token(token)




        
    