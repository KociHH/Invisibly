from typing import Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Query
from fastapi.responses import HTMLResponse
import logging
from fastapi import Depends
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep, oauth2_scheme
from jose import jwt
from app.crud.user import RedisJsonsProcess, UserProcess
from app.services.modules.profile.service import ProfileService
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from app.schemas.user import UserEditProfileNew, UserProfile
from shared.services.tools.other import full_name_constructor
from app.services.http_client import _http_client

router = APIRouter()
logger = logging.getLogger(__name__)

profile_service = ProfileService()

@router.get("/data", response_model=UserProfile)
async def user_profile_data(
    user_process: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    return await profile_service.user_profile_data.route(user_process)

@router.get("/edit/data")
async def user_edit_profile_data(
    user_process: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    return await profile_service.user_edit_profile_data.route(user_process)

@router.post("/edit", response_model=SuccessMessageAnswer)
async def processing_edit_profile(
    user: UserEditProfileNew, 
    user_process: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    return await profile_service.processing_edit_profile.route(user, user_process)


