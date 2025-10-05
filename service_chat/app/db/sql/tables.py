from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Index, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator
from datetime import datetime

base = declarative_base()

class UserChat(base):
    """
    user1_id: int
    user2_id: int
    created_at: datetime
    """
    
    __tablename__ = 'userChats'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user1_id: Mapped[int] = mapped_column(ForeignKey("userRegistered.user_id", ondelete="CASCADE"), nullable=False)
    user2_id: Mapped[int] = mapped_column(ForeignKey("userRegistered.user_id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user1_id', 'user2_id', name='uq_user1_user2'),
    )

    uid = relationship("UserRegistered", foreign_keys=[user1_id, user2_id])
    messages = relationship(
        "Message",
        back_populates="userChats", 
        cascade="all, delete-orphan"
    )
    
class Message(base):
    """
    chat_id: int
    sender_id: int
    content: str
    created_at: datetime
    """
    
    __tablename__ = 'messages'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("userChats.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("userRegistered.user_id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    send_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    chat = relationship("UserChat", back_populates="messages")
    uid = relationship("UserRegistered")
    __table_args__ = (
        Index('ix_messages_chat_send', 'chat_id', 'send_at'),
    )