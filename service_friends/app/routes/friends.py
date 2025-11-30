from fastapi import APIRouter, HTTPException, Request
import logging
from sqlalchemy import and_
from fastapi import Depends
from app.services.modules.friends.service import FriendsService
from app.crud.dependencies import get_current_user_dep, require_existing_user_dep
from shared.schemas.response_model import SuccessAnswer, SuccessMessageAnswer
from app.schemas.user import FriendAdd, FriendDelete
from app.db.sql.settings import get_db_session
from app.crud.user import RedisJsonsProcess, UserProcess

router = APIRouter()
logger = logging.getLogger(__name__)

friends_service = FriendsService()

@router.get("/data", response_model=SuccessAnswer)
async def user_friends_data(
    user_process: UserProcess = Depends(get_current_user_dep),
    ):
    return await friends_service.user_friends_data.route(user_process)

@router.post("/add")
async def processing_friend_add(
    fa: FriendAdd,
    user_process: UserProcess = Depends(get_current_user_dep),
):
    return await friends_service.processing_friend_add.route(fa, user_process)

@router.post("/delete")
async def processing_friend_delete(
    fd: FriendDelete,
    user_process: UserProcess = Depends(get_current_user_dep),
):
    return await friends_service.processing_friend_delete.route(fd, user_process)