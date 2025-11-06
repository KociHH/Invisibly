from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Index, MetaData, String, \
    Integer, DateTime, UniqueConstraint, Sequence, Identity
from typing import AsyncGenerator
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SERVICE_CHAT_NAME_SCHEMA = os.getenv("SERVICE_CHAT_NAME_SCHEMA")

base = declarative_base(metadata=MetaData(SERVICE_CHAT_NAME_SCHEMA))


class UserChat(base):
    """
    chat_id: int
    created_at: datetime
    """
    
    __tablename__ = "userChats"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    participants = relationship(
        "ChatParticipant", 
        back_populates="chat", 
        cascade="all, delete-orphan",
        passive_deletes=True
        )

class ChatParticipant(base):
    """
    id: int
    chat_id: int (отношение userChats.chat_id)
    user_id: int
    """
    
    __tablename__ = "chatParticipants"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("userChats.chat_id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
        )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    chat = relationship("UserChat", back_populates="participants")
    
    __table_args__ = (
        UniqueConstraint("chat_id", "user_id", name="uq_chat_user"),
    )

class Message(base):
    """
    message_id: int
    chat_id: int (отношение userChats.chat_id)
    participant_id: int (отношение chatParticipants.id)
    content: str
    viewed_at: datetime
    created_at: datetime
    send_at: datetime
    """
    
    __tablename__ = 'messages'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("userChats.chat_id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
        )
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("chatParticipants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    viewed_at: Mapped[bool] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    send_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    participant = relationship("ChatParticipant", back_populates="messages")
    
    __table_args__ = (
        Index("ix_messages_chat_send_at", "chat_id", "send_at"),
        Index("ix_messages_participant_send_at", "participant_id", "send_at"),
        UniqueConstraint("chat_id", "message_id", name="uq_messages_chat_message_id"),
    )