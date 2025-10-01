from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config.env import POSTGRES_URL
from sqlalchemy import Index, create_engine, select, pool, Sequence
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator
from datetime import datetime
import sqlalchemy.orm as so

base = declarative_base()

class FrozenAccounts(base):
    """
    user_id: int
    frozen_at: datetime
    delete_at: datetime
    """
    __tablename__ = 'frozenAccounts'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("userRegistered.user_id"), unique=True, nullable=False)
    frozen_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    delete_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    uid = relationship('UserRegistered')