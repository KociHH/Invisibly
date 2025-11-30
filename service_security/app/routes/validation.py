import re
from fastapi import APIRouter, HTTPException, Body
from fastapi.params import Query
from fastapi.responses import HTMLResponse
import logging
import uuid
from fastapi import Depends
from httpx import get
from app.services.modules.validation.service import ValidationService
from shared.config.variables import path_html, PSWD_context, curretly_msk
from app.crud.user import UserProcess
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep, oauth2_scheme
from app.schemas.code import SendCode, ConfirmPassword
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from app.services.rabbitmq.client import EmailRpcClient
from app.services.jwt import decode_jwt_token, create_token
from datetime import timedelta
from app.crud.user import RedisJsonsProcess
from app.db.redis.keys import RedisUserKeys
from app.services.http_client import _http_client

logger = logging.getLogger(__name__)
router = APIRouter()

validation_service = ValidationService()

@router.get("/confirm_code/data")
# 1. /confirm_code?cause=... 2. /confirm_code?cause=...&resend=...?
async def confirm_code_data(
    cause: str = Query(..., description="Причина вызова confirm_code"),
    user_process: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    return await validation_service.confirm_code_data.route(user_process)

@router.get("/resend_code")
async def resend_code(
    user_process: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    return await validation_service.resend_code.route(user_process)

@router.post("/confirm_code", response_model=SuccessAnswer)
async def confirm_code(
    rc: SendCode, 
    user_process: UserProcess = Depends(require_existing_user_dep)
    ):
    return await validation_service.confirm_code.route(rc, user_process)

# password not working
@router.post("/confirm_password", response_model=SuccessMessageAnswer)
async def processing_password(
    sp: ConfirmPassword,
    user_process: UserProcess = Depends(get_current_user_dep),
): 
    return await validation_service.confirm_password.route(sp, user_process)


