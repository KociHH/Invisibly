import os
from dotenv import set_key, find_dotenv
import secrets
import logging
from config.env import SECRET_KEY, SECRET_KEY_SIZE
from config.variables import ALGORITHM
from jose import jwt, exceptions
from fastapi import HTTPException

logger = logging.getLogger(__name__)

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
    """
    Декодирует JWT токен и возвращает его *dict

    Также если истек токен то вызывает исключение:
    raise HTTPException(
        status_code=401,
        detail="Invalid or expired token"
        )

    """
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=[algorithms])
        return decoded_token
    except exceptions.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


