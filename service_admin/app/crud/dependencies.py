from httpx import get
from shared.crud.sql.dependencies import require_existing_user, get_current_user
from app.db.sql.settings import get_db_session
from shared.services.http_client.variables import get_http_client_state
from fastapi.security import OAuth2PasswordBearer
from shared.services.jwt.token import cre

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

get_current_user_dep = get_current_user(get_db_session)
require_existing_user_dep = require_existing_user(get_db_session, get_http_client_state)