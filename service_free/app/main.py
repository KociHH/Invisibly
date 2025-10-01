from jose import jwt
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
import logging
import uvicorn
from app.routes import auth, root, data
from config.env import UHOST, UPORT
from fastapi.staticfiles import StaticFiles
from app.db.sql.settings import engine
from app.db.sql.tables import base
from contextlib import asynccontextmanager
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from shared.services.tools.limits import limiter
from shared.services.middleware import MiddlewareProcess
import asyncio
from app.services.rabbitmq.server import start_rpc_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
    
    # rpc_server_task = asyncio.create_task(start_rpc_server())
    # logger.info("RPC server startup initiated.")
    yield
    
    # rpc_server_task.cancel()
    # try:
    #     await rpc_server_task
    # except asyncio.CancelledError:
    #     logger.info("RPC server shutdown completed.")
    # logger.info("RPC server shutdown initiated.")
    # logger.info("Application lifespan ending.")

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    middle = MiddlewareProcess(request)
    return middle.ratelimit_handler(exc)

app.add_middleware(SlowAPIMiddleware)

app.mount("/static", StaticFiles(directory="app/frontend/dist/ts"), name="static")
app.include_router(auth.router)
app.include_router(root.router)
app.include_router(data.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)