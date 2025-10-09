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

SERVICE_FRIENDS_NAME_SCHEMA = os.getenv("SERVICE_FRIENDS_NAME_SCHEMA")

base = declarative_base(metadata=MetaData(SERVICE_FRIENDS_NAME_SCHEMA))


class FriendUser(base):
    """
    user_id: int
    friend_id: int
    addition_number: int
    """
    __tablename__ = 'friendsUser'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    friend_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    addition_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("user_id", "friend_id", name="uq_user_friend"),
        UniqueConstraint("user_id", "addition_number", name="uq_user_addition"),
        Index("ix_user_addition", "user_id", "addition_number")
    )

class SendFriendRequest(base):
    """
    user_id: int
    request_user_id: int
    send_at: datetime
    """
    __tablename__ = 'sendFriendRequests'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=False, nullable=False, index=True)
    request_user_id: Mapped[int] = mapped_column(Integer, unique=False, nullable=False, index=True) 
    send_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("user_id", "request_user_id", name="uq_user_request"),
        Index("ix_user_send_at", "user_id", "send_at")
    )