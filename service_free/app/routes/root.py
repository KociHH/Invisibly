from fastapi import APIRouter, HTTPException, Request
import logging
from app.services.modules.root.service import RootService
from shared.config.variables import path_html, PSWD_context
from app.crud.user import GetUserInfo

router = APIRouter()
logger = logging.getLogger(__name__)

root_service = RootService()

@router.get("/")
async def root_page(request: Request):
    return root_service.root.route(request)