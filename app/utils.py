from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.backend.data.sql import UserRegistered
import uuid
import logging

logger = logging.getLogger(__name__)
PSWD_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

