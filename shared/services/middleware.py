from jose import jwt
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
import logging
from config.env import SECRET_KEY, ALGORITHM
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from shared.services.tools.limits import limiter

logger = logging.getLogger(__name__)

class MiddlewareProcess:
    def __init__(self, request: Request) -> None:
        self.request = request

    async def access_token_middleware(self, call_next, excluded_paths: list):
        excluded_paths += ["/login", "/register", '/']
        public_paths = excluded_paths
        if any(self.request.url.path.startswith(p) for p in public_paths):
            response = await call_next(self.request)
            return response

        auth_header = self.request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if token:
            try:
                payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                self.request.state.user_id = payload.get("user_id")
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
                logger.warning(f"Ошибка в функции access_token_middleware:\n {e}")
                self.request.state.user_id = None
                return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        if not getattr(self.request.state, "user_id", None):
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

        response = await call_next(self.request)
        return response

    async def ratelimit_handler(self, exc: RateLimitExceeded):
        headers = {
            "Retry-After": "10",
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Remaining": "0",
        }
        return JSONResponse(status_code=429, content={"detail": "Too many requests"}, headers=headers)