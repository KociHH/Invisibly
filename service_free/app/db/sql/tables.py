from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config import POSTGRES_URL
from sqlalchemy import Index, create_engine, select, pool, Sequence
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator
from datetime import datetime

base = declarative_base()

class UserRegistered(base):
    """
    user_id: int
    password: str
    login: str
    name: str
    surname: str
    email: str
    email_hash: str
    registration_date: datetime
    bio: str
    """

    __tablename__ = 'userRegistered'

    user_id: Mapped[int] = mapped_column(
        Integer, 
        Sequence('user_id', start=1000, increment=1),
        primary_key=True, 
        )
    login: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email_hash: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    registration_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    bio: Mapped[str] = mapped_column(String, nullable=True)