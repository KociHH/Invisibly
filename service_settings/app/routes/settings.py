from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import logging
from app.schemas.account import SettingsExit
from app.crud.user import UserProcess
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.db.sql.settings import get_db_session
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep, oauth2_scheme
from app.services.http_client import _http_client
from app.services.modules.settings.service import SettingsService

router = APIRouter()
logger = logging.getLogger(__name__)
    
settings_service = SettingsService()
    
@router.get("/settings/data")
async def user_settings_data(
    user_process: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    return await settings_service.user_settings_data.route(user_process)

@router.post("/logout")
async def user_logout(
    se: SettingsExit,
    user_process: UserProcess = Depends(require_existing_user_dep)
    ):
    return await settings_service.user_logout.route(se, user_process)

