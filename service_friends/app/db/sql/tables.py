from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config import POSTGRES_URL
from sqlalchemy import Index, create_engine, select, pool, Sequence
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator
from datetime import datetime

base = declarative_base()

class FriendsUser(base):
    """
    user_id: int
    friend_id: int
    addition_number: int
    """
    __tablename__ = 'friendsUser'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("userRegistered.user_id"), unique=False, nullable=False)
    friend_id: Mapped[int] = mapped_column(ForeignKey("userRegistered.user_id"), nullable=False)
    addition_number: Mapped[int] = mapped_column(Integer, nullable=False)

    uid = relationship('UserRegistered', foreign_keys=[user_id, friend_id])

class SendFriendRequests(base):
    """
    user_id: int
    request_user_id: int
    send_at: datetime
    """
    __tablename__ = 'sendFriendRequests'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("userRegistered.user_id"), unique=False, nullable=False)
    request_user_id: Mapped[int] = mapped_column(ForeignKey("userRegistered.user_id"), unique=False, nullable=False) 
    send_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    uid = relationship('UserRegistered', foreign_keys=[user_id, request_user_id])