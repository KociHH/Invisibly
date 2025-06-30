from fastapi import FastAPI
import logging
from app.backend.api import auth, user, root
import uvicorn
from config.env import UHOST, UPORT
from fastapi.staticfiles import StaticFiles
from app.backend.data.sql import base, engine
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/frontend/dist/ts"), name="static")
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(root.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)