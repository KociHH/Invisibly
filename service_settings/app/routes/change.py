from fastapi import APIRouter, HTTPException, Body
import logging
from fastapi import Depends
from app.crud.user import EncryptEmailProcess, UserProcess, RedisJsonsProcess
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from app.schemas.change import ChangeEmail, SendPassword
from app.services.modules.change.service import ChangeService
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer


logger = logging.getLogger(__name__)
router = APIRouter()

change_service = ChangeService()

@router.post("/change/email", response_model=SuccessMessageAnswer)
async def change_email(
    change: ChangeEmail,
    user_process: UserProcess = Depends(require_existing_user_dep)
):
    return await change_service.change_email.route(change, user_process)

