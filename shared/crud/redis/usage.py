from email.policy import HTTP
from http import server
from typing import Any
from shared.crud.redis.create import RedisJsonsServerToken
from shared.services.jwt.exceptions import UNAUTHORIZED
from shared.services.jwt.token import create_disposable_interservice_token, SECRET_KEY, ALGORITHM
from shared.config.variables import curretly_msk
from jose import jwt, exceptions
from shared.crud.redis.create import RedisJsonsServerToken
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def create_add_interservice_token(data: dict) -> dict:
    token, jti = create_disposable_interservice_token(data=data)
    redis_instance = RedisJsonsServerToken(jti)
    result = redis_instance.save_interservice_token(
        token=token,
        )
    if not result:
        raise HTTPException(status_code=403, detail="This token is already in use")
    return result

def verify_interservice_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except exceptions.ExpiredSignatureError:
        logger.info("Межсервисный токен истек")
        raise UNAUTHORIZED
    except exceptions.JWTError:
        raise UNAUTHORIZED
        
    token_type: str = payload.get("type")
    if token_type != "interservice":
        raise UNAUTHORIZED
    
    jti = payload.get("jti")
    if not jti:
        raise UNAUTHORIZED
    
    server_token = RedisJsonsServerToken(jti)
    check_token = server_token.get_interservice_token()
        
    if check_token:
        return payload
    else:
        raise UNAUTHORIZED




        
    