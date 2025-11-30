from fastapi import APIRouter, Depends, HTTPException, Query, status
import logging
from app.schemas.data import FriendsRequestsInfo
from app.services.modules.export.service import ExportService
from shared.crud.redis.create import RedisJsonsServerToken
from shared.crud.redis.dependencies import get_interservice_token_info
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.sql.settings import get_db_session
from typing import Annotated

router = APIRouter()
logger = logging.getLogger(__name__)

export_service = ExportService()

@router.get("/friends_requests_info")
async def friends_requests_info_get(
    fri: Annotated[FriendsRequestsInfo, Query()],
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
   return await export_service.friends_requests_info_get.route(fri, token_info, db_session)