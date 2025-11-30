from jose import jwt
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
import logging
import uvicorn
from app.routes import profile
from app.db.sql.settings import get_db_session
from contextlib import asynccontextmanager
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from service_profile.app.routes import profile_user
from shared.services.tools.limits import limiter
from shared.services.middleware import MiddlewareProcess
from app.services.http_client import _http_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = _http_client.free
    yield

    await app.state.http_client.close()
    logger.info("Service stoped!")

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    middle = MiddlewareProcess(request)
    return middle.ratelimit_handler(exc)

app.add_middleware(SlowAPIMiddleware)

app.include_router(profile.router, prefix="/api/profile")
app.include_router(profile_user.router, prefix="/api/profile")
