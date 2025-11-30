from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Query
import logging
from app.crud.user import UserProcess
from app.services.modules.profile_user.service import ProfileUserService
from fastapi import Depends
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.sql.settings import get_db_session

router = APIRouter(prefix="/user")
logger = logging.getLogger(__name__)

profile_user_service = ProfileUserService()

@router.get("/data")
async def friend_profile_data(
    profile_id: str = Query(..., description='id профиля пользователя'),
    user_process: UserProcess = Depends(get_current_user_dep),
):
    return await profile_user_service.friend_profile_data.route(profile_id)


@router.post("/")
async def processing_friend_profile(
    user_info: UserProcess = Depends(get_current_user_dep),
    db_session: AsyncSession = Depends(get_db_session),
):
    return await profile_user_service.processing_friend_profile.route()