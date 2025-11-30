from sqlalchemy.ext.asyncio import AsyncSession
import logging
from kos_Htools.sql.sql_alchemy import BaseDAO
from app.services.jwt import generate_jwt_secretkey
from shared.config.variables import curretly_msk
from config import TOKEN_LIFETIME_DAYS
from datetime import timedelta
from app.db.sql.tables import SecretKeyJWT

logger = logging.getLogger(__name__)

