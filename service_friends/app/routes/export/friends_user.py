from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.sql.settings import get_db_session
from app.schemas.data import FriendFilter, FriendFullInfo, FriendUpdate, GetOrCacheFriends
from app.services.modules.export.service import ExportService
from shared.crud.redis.create import RedisJsonsServerToken
from shared.crud.redis.dependencies import get_interservice_token_info
from shared.services.jwt.exceptions import UNAUTHORIZED

router = APIRouter()
logger = logging.getLogger(__name__)

export_service = ExportService()

@router.get("/find_friend_by_param")
async def find_friend_by_param_get(
    uf: Annotated[FriendFilter, Query()],
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session),
):
    return await export_service.find_friend_by_param_get.route(uf, token_info, db_session)

@router.get("/get_friend_info")
async def get_friend_info_get(
    ufi: Annotated[FriendFullInfo, Query()],
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session),
):
    return await export_service.get_friend_info_get.route(ufi, token_info, db_session)
    
@router.patch('/update_friend')
async def update_friend_patch(
    user_update: FriendUpdate,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session),
):
    return await export_service.update_friend_patch.route(user_update, token_info, db_session)

@router.patch("/get_or_cache_friends")
async def get_or_cache_friends_patch(
    gocf: GetOrCacheFriends,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session),
):
    return await export_service.get_or_cache_friends_patch.route(gocf, token_info, db_session)