from jose import jwt
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
import logging
import uvicorn
from app.routes import tokens, validation, data
from config import UHOST, UPORT
from fastapi.staticfiles import StaticFiles
from app.db.sql.settings import engine
from app.db.sql.tables import base
from contextlib import asynccontextmanager
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from shared.services.tools.limits import limiter
from shared.services.middleware import MiddlewareProcess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    middle = MiddlewareProcess(request)
    return middle.ratelimit_handler(exc)

app.add_middleware(SlowAPIMiddleware)

app.mount("/static", StaticFiles(directory="app/frontend/dist/ts"), name="static")
app.include_router(tokens.router)
app.include_router(validation.router)
app.include_router(data.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)