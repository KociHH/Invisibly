from datetime import datetime, timedelta
from jose import jwt, exceptions
from fastapi import HTTPException, status
from config.env import SECRET_KEY, REFRESH_TOKEN_LIFETIME_DAYS, ACCESS_TOKEN_LIFETIME_MINUTES
from config.variables import ALGORITHM, curretly_msk
import logging
import uuid

logger = logging.getLogger(__name__)
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Unable to verify credentials",
    headers={"Authenticate": "Bearer"},
)

# check
def verify_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return user_id
    except exceptions.JWTError:
        raise credentials_exception
    
def verify_refresh_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id: int = payload.get("user_id")
        token_type: str = payload.get("type")
        jti: str = payload.get("jti")
        if user_id is None or token_type != "refresh" or jti is None:
            raise credentials_exception
        return user_id, jti
    except exceptions.JWTError:
        raise credentials_exception
# create
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
