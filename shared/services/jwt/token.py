from datetime import timedelta
import logging
from shared.services.tools.other import l
from shared.config.variables import curretly_msk
from jose import jwt, exceptions
from fastapi import HTTPException, status
from shared.config.variables import curretly_msk
import logging

logger = logging.getLogger(__name__)

ACCESS_TOKEN_LIFETIME_MINUTES = int(l("ACCESS_TOKEN_LIFETIME_MINUTES"))
REFRESH_TOKEN_LIFETIME_DAYS = int(l("REFRESH_TOKEN_LIFETIME_DAYS"))
ALGORITHM = l("ALGORITHM")
SECRET_KEY = l("SECRET_KEY")
SECRET_KEY_SIZE = int(l("SECRET_KEY_SIZE"))
TOKEN_LIFETIME_DAYS = int(l("TOKEN_LIFETIME_DAYS"))

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Unable to verify credentials",
    headers={"Authenticate": "Bearer"},
    )

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

def verify_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise UNAUTHORIZED
        return user_id

    except exceptions.JWTError:
        raise UNAUTHORIZED