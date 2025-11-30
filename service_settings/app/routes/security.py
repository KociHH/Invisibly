from datetime import timedelta
from operator import ge
from typing import Any
from fastapi import APIRouter, HTTPException, Request
import logging
from httpx import get
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep, oauth2_scheme
from fastapi import Depends
from jose import jwt
from app.schemas.account import DeleteAccount
from app.schemas.change import ChangePassword
from app.schemas.change import ChangeEmailForm
from app.schemas.response_model import EmailSendVerify
from app.services.modules.security.service import SecurityService
from shared.schemas.response_model import SuccessMessageAnswer, SuccessAnswer
from app.crud.user import EncryptEmailProcess, UserProcess, RedisJsonsProcess

logger = logging.getLogger(__name__)
router = APIRouter()

security_service = SecurityService()

@router.get("/change_email/data")
async def change_email_data(
    user_process: UserProcess = Depends(get_current_user_dep),
    token: str = Depends(oauth2_scheme)
    ):
    return await security_service.change_email_data.route(user_process)

@router.post("/change_email", response_model=EmailSendVerify)
async def processing_email(
    cef: ChangeEmailForm, 
    user_process: UserProcess = Depends(get_current_user_dep)
):
    return await security_service.processing_email.route(cef, user_process)
    
@router.post("/change_password", response_class=SuccessMessageAnswer)
async def processing_password(
    np: ChangePassword,
    user_process: UserProcess = Depends(get_current_user_dep),
):
    return await security_service.processing_password.route(np, user_process)
 
@router.post("/delete_account", response_model=SuccessMessageAnswer)
async def processing_delete(
    da: DeleteAccount,
    user_process: UserProcess = Depends(require_existing_user_dep),
):
    return await security_service.processing_delete.route(da, user_process)