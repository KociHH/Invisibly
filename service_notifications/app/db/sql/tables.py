from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Index, MetaData, create_engine, select, pool, Sequence
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator
from datetime import datetime
from config import SERVICE_NOTIFICATIONS_NAME_SCHEMA

base = declarative_base(metadata=MetaData(SERVICE_NOTIFICATIONS_NAME_SCHEMA))


class NotificationSystem(base):
    """
    text: str
    type_log: str
    error_log: int
    user_id: int
    send_at: datetime
    read_at: bool
    """
    __tablename__ = 'notificationSystem'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    type_log: Mapped[str] = mapped_column(String, nullable=False)
    error: Mapped[int] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    send_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    read_at: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

class NotificationUser(base):
    """
    text: str
    type_log: str
    user_id: int
    send_at: datetime
    read_at: bool
    """

    __tablename__ = 'notificationUser'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    type_log: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    send_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    read_at: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)