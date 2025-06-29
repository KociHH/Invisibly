from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config.env import POSTGRES_URL
from sqlalchemy import create_engine, select, pool, Sequence
from sqlalchemy.orm import declarative_base, relationship
import logging
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator

base = declarative_base()

engine = create_async_engine(url=POSTGRES_URL, echo=False, future=True, poolclass=pool.NullPool)
session_engine = async_sessionmaker(engine, expire_on_commit=False,  class_=AsyncSession)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_engine() as session:
        yield session

class UserRegistered(base):
    __tablename__ = 'user_registered'

    id = Column(
        BigInteger, 
        Sequence('user_id_seq', start=1000, increment=1),
        primary_key=True, 
        )
    password = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=True)