from typing import Any
from fastapi import Depends
from shared.crud.redis.create import RedisJsonsServerToken
from shared.crud.redis.usage import verify_interservice_token
from shared.services.jwt.exceptions import UNAUTHORIZED
import logging
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

oauth2_scheme = HTTPBearer()

def get_interservice_token_info(
    creds: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    token = creds.credentials
    payload = verify_interservice_token(token)
    if payload:
        jti = payload.get("jti")
        server_token = RedisJsonsServerToken(jti)
        server_token.payload = payload
        
        return server_token
    raise UNAUTHORIZED