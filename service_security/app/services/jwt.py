from datetime import datetime, timedelta
import secrets
import uuid
from dotenv import find_dotenv, set_key
from jose import jwt, exceptions
from fastapi import HTTPException, status
from config import SECRET_KEY, REFRESH_TOKEN_LIFETIME_DAYS, ACCESS_TOKEN_LIFETIME_MINUTES, SECRET_KEY_SIZE, ALGORITHM
from shared.config.variables import curretly_msk
from config import ALGORITHM
import logging

logger = logging.getLogger(__name__)

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Unable to verify credentials",
    headers={"Authenticate": "Bearer"},
    )

def verify_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise UNAUTHORIZED
        return user_id

    except exceptions.JWTError:
        raise UNAUTHORIZED

def verify_refresh_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id: int = payload.get("user_id")
        token_type: str = payload.get("type")
        jti: str = payload.get("jti")
        if user_id is None or token_type != "refresh" or jti is None:
            raise UNAUTHORIZED
        return user_id, jti
    except exceptions.JWTError:
        raise UNAUTHORIZED

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

def generate_jwt_secretkey(recording_env: bool = False, env_path: str = ".env") -> None | str:
    dotenv_path = find_dotenv(env_path)
    new_secret_key = secrets.token_hex(SECRET_KEY_SIZE)
    
    if recording_env:
        if dotenv_path:
            set_key(dotenv_path, 'JWT_SECRET_KEY', new_secret_key)
            return new_secret_key
        else:
            logger.error(f"Не найден заданный путь к env: {env_path}")
            return
    else:
        return new_secret_key
    
def decode_jwt_token(token: str, secret_key: str = SECRET_KEY, algorithms: str = ALGORITHM) -> dict:
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=[algorithms])
        return decoded_token
    except exceptions.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )