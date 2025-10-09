from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Index, MetaData, create_engine, select, pool, Sequence
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SERVICE_SETTINGS_NAME_SCHEMA = os.getenv("SERVICE_SETTINGS_NAME_SCHEMA")

base = declarative_base(metadata=MetaData(SERVICE_SETTINGS_NAME_SCHEMA))


class FrozenAccounts(base):
    """
    user_id: int
    frozen_at: datetime
    delete_at: datetime
    """
    __tablename__ = 'frozenAccounts'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    frozen_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    delete_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)