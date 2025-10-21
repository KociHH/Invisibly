from datetime import timedelta
import logging
import re
from typing import Any, Tuple
import uuid
from shared.services.jwt.exceptions import UNAUTHORIZED
from shared.services.tools.other import l
from shared.config.variables import curretly_msk
from jose import jwt, exceptions
from fastapi import HTTPException
from shared.config.variables import curretly_msk
import logging
from shared.data.redis.instance import __redis_save_jwt_code_token__
from shared.services.tools.variables import names_services
from shared.crud.redis.usage import verify_interservice_token


logger = logging.getLogger(__name__)

ACCESS_TOKEN_LIFETIME_MINUTES = int(l("ACCESS_TOKEN_LIFETIME_MINUTES"))
REFRESH_TOKEN_LIFETIME_DAYS = int(l("REFRESH_TOKEN_LIFETIME_DAYS"))
INTERSERVICE_TOKEN_LIFETIME_MINUTES = int(l("HTTP_TOKEN_LIFETIME_MINUTES"))
ALGORITHM = [l("ALGORITHM")]
SECRET_KEY = l("SECRET_KEY")
SECRET_KEY_SIZE = int(l("SECRET_KEY_SIZE"))
TOKEN_LIFETIME_DAYS = int(l("TOKEN_LIFETIME_DAYS"))

def create_default_time_jwt(
    token_type: str, 
    expire_delta: int | str | None,
    ):
    """
    return: expires_at, issued_at
    """
    
    if token_type == "access":
        term = timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
    elif token_type == "refresh":
        term = timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS)
    else:
        logger.warning(f"Нет такого типа токена: {token_type}")
        return

    issued_at = curretly_msk()

    if expire_delta:
        expires_at = issued_at + expire_delta
    else:
        expires_at = issued_at + term
        
    return expires_at, issued_at

def verify_token_user(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise UNAUTHORIZED
        return user_id

    except exceptions.JWTError:
        raise UNAUTHORIZED
    
def create_disposable_interservice_token(data: dict):
    """
    Пример необходимых параметров data:
    
    {
        "iss": "SERVICE_A",
        "aud": "SERVICE_B",
        "scopes": ["read", "write"]
    }
    """
    need_scopes = ["read", "write", "delete"]
    
    for param in ["scopes", "iss", "aud"]:
        if param not in data:
            logger.error(f"Отсутствует параметр {param} в данных: {data}")
            raise HTTPException(status_code=400, detail=f"Missing parameter: {param}")
    
    scopes = data.get("scopes", [])
    iss = data.get("iss", "")
    aud = data.get("aud", "")
    
    for valid_param, value in [("scopes", scopes), ("iss", iss), ("aud", aud)]:
        if not value:
            logger.error(f"Параметр {valid_param} имеет значение None: {data}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {valid_param}")
        if valid_param == "scopes" and not isinstance(value, list):
            logger.error(f"Параметр {valid_param} должен быть списком: {data}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter type: {valid_param}")
        if valid_param in ["iss", "aud"] and not isinstance(value, str):
            logger.error(f"Параметр {valid_param} должен быть строкой: {data}")
            raise HTTPException(status_code=400, detail=f"Invalid parameter type: {valid_param}")
        
    for scope in scopes:
        if scope not in need_scopes:
            logger.error(f"Неизвестный scope: {scope}")
            raise HTTPException(status_code=400, detail="Unknown scope")

    if iss.upper() not in names_services:
        logger.error(f"Неизвестный issuer: {iss}")
        raise HTTPException(status_code=400, detail="Unknown issuer")
    
    term = timedelta(minutes=INTERSERVICE_TOKEN_LIFETIME_MINUTES)
    exp = curretly_msk() + term
    jti = str(uuid.uuid4())
    token_type = "interservice"
    
    to_encode = data.copy()
    to_encode.update({
        "iss": iss,
        "aud": aud,
        "exp": exp, 
        "type": token_type,
        "scopes": scopes,
        "jti": jti
        })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, jti
    
def control_rules_interservice_token(
    payload: dict[str, Any] | None, 
    token: str | None = None,
    required_scopes: list[str] | None = None,
    ) -> Tuple[bool, bool, bool]:
    """
    token: если не указан payload, то проверяются scopes из токена
    
    required_scopes: если не указан payload, то проверяются scopes из токена
    
    return: write, delete, read
    """
    
    if not payload:
        if not token:
            logger.error("Отсутствует токен для проверки")
            raise UNAUTHORIZED
        try:
            payload = verify_interservice_token(token)
        except exceptions.ExpiredSignatureError:
            logger.info(f"Межсервисный токен истек")
            raise UNAUTHORIZED
        except Exception as e:
            logger.error(f"Ошибка проверки межсервисного токена: {e}")
            raise HTTPException(status_code=401, detail="Invalid interservice token")
    
    if required_scopes:
        for scope in required_scopes:
            if scope not in payload.get("scopes", []):
                logger.error(f"Отсутствует необходимый scope: {scope}")
                raise UNAUTHORIZED
    
    scopes = payload.get("scopes", [])
    if not isinstance(scopes, list):
        scopes = list(scopes) if scopes is not None else []
    
    write = "write" in scopes
    delete = "delete" in scopes
    read = "read" in scopes
    
    return write, delete, read

def get_interservice_token_not_verify_exp(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM, options={"verify_exp": False})
        return payload
    except Exception as e:
        logger.error(f"Ошибка проверки межсервисного токена: {e}")
        raise UNAUTHORIZED