from jose import jwt
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
import logging
from app.backend.api import auth, root
from app.backend.api.tools.security import tokens, other
from app.backend.api.user import profile, settings, chats
import uvicorn
from app.backend.api.user.settings import security
from config.env import UHOST, UPORT
from fastapi.staticfiles import StaticFiles
from app.backend.data.sql.tables import base, engine
from contextlib import asynccontextmanager
from app.backend.celery.tasks import check_jwt_token_date
from config.env import SECRET_KEY
from config.variables import ALGORITHM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    check_jwt_token_date.delay()
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def access_token_middleware(request: Request, call_next):
    public_paths = ["/login", "/register", '/']
    if any(request.url.path.startswith(p) for p in public_paths):
        response = await call_next(request)
        return response

    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if token:
        try:
            payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_id = payload.get("user_id")
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            logger.warning(f"Ошибка в функции access_token_middleware:\n {e}")
            request.state.user_id = None

    response = await call_next(request)
    return response

app.mount("/static", StaticFiles(directory="app/frontend/dist/ts"), name="static")
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(security.router)
app.include_router(settings.router)
app.include_router(chats.router)
app.include_router(root.router)
app.include_router(tokens.router)
app.include_router(other.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)