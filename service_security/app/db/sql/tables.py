from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config import POSTGRES_URL
from sqlalchemy import Index, create_engine, select, pool, Sequence
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator
from datetime import datetime

base = declarative_base()
    
class UserJWT(base):
    """
    id: int
    user_id: int
    jti: str
    issued_at: datetime 
    expires_at: datetime
    revoked: bool
    token_type: str
    """
    __tablename__ = 'userJWT'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('userRegistered.user_id'), unique=False, nullable=False)
    jti: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=True)
    token_type: Mapped[str] = mapped_column(String, nullable=False)

    uid = relationship('UserRegistered')