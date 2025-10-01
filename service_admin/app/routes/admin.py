from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import logging
from app.crud.user import UserProcess
from config.variables import path_html
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from service_chat.app.db.sql.settings import get_db_session
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.crud.dependencies import template_not_found_user
from service_chat.app.crud.user import ChatsProcess

router = APIRouter()
logger = logging.getLogger(__name__)