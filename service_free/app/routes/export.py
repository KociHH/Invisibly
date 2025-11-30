from fastapi import APIRouter, Depends, HTTPException, Query
import logging
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import RedisJsonsProcess, UserProcess
from app.services.modules.export.service import ExportService
from shared.crud.redis.dependencies import get_interservice_token_info
from app.db.sql.settings import get_db_session
from app.schemas.export import FindUserByParam, UserFullInfo, UserUpdate, GetOrCacheUserInfo
from shared.crud.redis.create import RedisJsonsServerToken
from shared.services.jwt.token import control_rules_interservice_token
from shared.services.jwt.exceptions import UNAUTHORIZED

router = APIRouter()
logger = logging.getLogger(__name__)

export_service = ExportService()

@router.get("/find_user_by_param")
async def find_user_by_param_get(
    fubp: Annotated[FindUserByParam, Query()],
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session),
):
    return await export_service.find_user_by_param.route(fubp, token_info, db_session)

@router.get("/get_user_info")
async def get_user_info_get(
    ufi: Annotated[UserFullInfo, Query()],
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    return await export_service.get_user_info.route(ufi, token_info, db_session)

@router.patch('/update_user')
async def update_user_patch(
    uu: UserUpdate,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session) 
):
    return await export_service.update_user.route(uu, token_info, db_session)

@router.patch("/get_or_cache_user_info")
async def get_or_cache_user_info_patch(
    gocui: GetOrCacheUserInfo,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    return await export_service.get_or_cache_user_info.route(gocui, token_info, db_session)