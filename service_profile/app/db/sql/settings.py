from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config import POSTGRES_URL
from sqlalchemy import pool
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, Integer, DateTime, UniqueConstraint
from typing import AsyncGenerator

engine = create_async_engine(url=POSTGRES_URL, echo=False, future=True, poolclass=pool.NullPool)
session_engine = async_sessionmaker(engine, expire_on_commit=False,  class_=AsyncSession)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_engine() as session:
        yield session