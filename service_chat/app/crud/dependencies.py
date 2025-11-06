from fastapi import HTTPException, WebSocket, status
from shared.crud.sql.dependencies import require_existing_user, get_current_user
from app.db.sql.settings import get_db_session
from shared.services.http_client.gateway import get_http_client_state
from fastapi.security import OAuth2PasswordBearer
from shared.services.jwt.token import verify_token_user
import logging

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


get_current_user_dep = get_current_user(get_db_session)
require_existing_user_dep = require_existing_user(get_db_session, get_http_client_state)

async def get_user_from_ws(ws: WebSocket) -> int:
    token = ws.query_params.get("token")
    if not token:
        await ws.close(reason="Token required")
        logger.error(f"Не передан token в параметрах websocket: {token}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WS token not found")

    user_id = verify_token_user(token)
    return user_id
