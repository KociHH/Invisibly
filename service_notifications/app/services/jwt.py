from datetime import datetime, timedelta
import uuid
from jose import jwt, exceptions
from fastapi import HTTPException, status
from config import SECRET_KEY, REFRESH_TOKEN_LIFETIME_DAYS, ACCESS_TOKEN_LIFETIME_MINUTES, ALGORITHM
from shared.config.variables import curretly_msk
import logging

logger = logging.getLogger(__name__)


def create_token(
        data: dict, 
        expire_delta: None | timedelta = None, 
        token_type: str = "access"
        ):
    if token_type == "access":
        term = timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
    elif token_type == "refresh":
        term = timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS)
    else:
        logger.warning(f"Нет такого типа токена: {token_type}")
        return

    to_encode = data.copy()
    if expire_delta:
        expire = curretly_msk() + expire_delta
    else:
        expire = curretly_msk() + term
    jti = str(uuid.uuid4())
    to_encode.update({
        "exp": expire, 
        "type": token_type, 
        "jti": jti
        })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, jti