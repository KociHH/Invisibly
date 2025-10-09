from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, MetaData, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator
from datetime import datetime
from config import SERVICE_ADMIN_NAME_SCHEMA

base = declarative_base(metadata=MetaData(SERVICE_ADMIN_NAME_SCHEMA))


class AdminControl(base):
    __tablename__ = "adminControl"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
