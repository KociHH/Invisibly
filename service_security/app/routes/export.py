from fastapi import APIRouter, Depends, HTTPException, Request
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.modules.export.service import ExportService
from shared.crud.redis.create import RedisJsonsServerToken
from shared.crud.redis.dependencies import get_interservice_token_info
from app.db.sql.settings import get_db_session
from app.schemas.export import CreateUJWT

router = APIRouter()
logger = logging.getLogger(__name__)

export_service = ExportService()

@router.post("/create_UJWT")
async def create_UJWT_post(
    cujwt: CreateUJWT,
    token_info: RedisJsonsServerToken = Depends(get_interservice_token_info),
    db_session: AsyncSession = Depends(get_db_session)
):
    return await export_service.create_userJWT_post.route(cujwt, token_info, db_session)