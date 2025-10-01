from datetime import datetime, timedelta
from jose import jwt, exceptions
from fastapi import HTTPException, status
from config.env import SECRET_KEY, REFRESH_TOKEN_LIFETIME_DAYS, ACCESS_TOKEN_LIFETIME_MINUTES
from config.variables import curretly_msk
from config.env import ALGORITHM
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