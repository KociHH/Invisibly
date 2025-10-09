from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, MetaData, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SERVICE_CELERY_NAME_SCHEMA = os.getenv("SERVICE_CELERY_NAME_SCHEMA")

base = declarative_base(metadata=MetaData(SERVICE_CELERY_NAME_SCHEMA))


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