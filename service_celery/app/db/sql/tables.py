from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config.env import POSTGRES_URL
from sqlalchemy import Index, create_engine, select, pool, Sequence
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator
from datetime import datetime

base = declarative_base()

class SecretKeyJWT(base):
    """
    secret_key: str
    created_key: datetime
    change_key: datetime
    """
    __tablename__ = 'secretKeyJWT'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    secret_key: Mapped[str] = mapped_column(String, nullable=False)
    created_key: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    change_key: Mapped[datetime] = mapped_column(DateTime, nullable=False)