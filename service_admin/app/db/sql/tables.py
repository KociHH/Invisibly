from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator
from datetime import datetime

base = declarative_base()

class AdminControl(base):
    __tablename__ = "adminControl"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, ForeignKey("userRegistered.user_id"), nullable=False)
