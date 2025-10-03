import asyncio
from jose import jwt
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
import logging
import uvicorn
from app.routes import notifications
from config import UHOST, UPORT
from fastapi.staticfiles import StaticFiles
from app.db.sql.settings import engine
from app.db.sql.tables import base
from contextlib import asynccontextmanager
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from shared.services.tools.limits import limiter
from shared.services.middleware import MiddlewareProcess
from app.services.rabbitmq.server import rabbit_init

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    rabbit_server = asyncio.create_task(rabbit_init())
    logger.info("RebbitMQ success init")
    yield

    rabbit_server.cancel()
    try:
        await rabbit_server
        logger.info("RabbitMQ success cancel")
    except asyncio.CancelledError:
        logger.info("RPC server shutdown completed.")

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    middle = MiddlewareProcess(request)
    return middle.ratelimit_handler(exc)

app.add_middleware(SlowAPIMiddleware)

app.mount("/static", StaticFiles(directory="app/frontend/dist/ts"), name="static")
app.include_router(notifications.router)
