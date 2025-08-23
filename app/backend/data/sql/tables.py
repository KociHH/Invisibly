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
    """
    user_id: int
    password: str
    login: str
    name: str
    surname: str
    email: str
    email_hash: str
    registration_date: datetime
    bio: str
    """

    __tablename__ = 'userRegistered'

    user_id = Column(
        BigInteger, 
        Sequence('user_id', start=1000, increment=1),
        primary_key=True, 
        )
    login = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    email_hash = Column(String, nullable=False, unique=True)
    registration_date = Column(DateTime, nullable=False)
    bio = Column(String, nullable=True)
    
class UserJWT(base):
    """
    id: int
    user_id: int
    jti: str
    issued_at: datetime 
    expires_at: datetime
    revoked: bool
    token_type: str
    """
    __tablename__ = 'userJWT'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('userRegistered.id'), unique=False, nullable=False)
    jti = Column(String, unique=True, nullable=False)
    issued_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, nullable=True)
    token_type = Column(String, nullable=False)

    uid = relationship('UserRegistered')

class SecretKeyJWT(base):
    """
    secret_key: str
    created_key: datetime
    change_key: datetime
    """
    __tablename__ = 'secretKeyJWT'
    
    secret_key = Column(String, nullable=False)
    created_key = Column(DateTime, nullable=False)
    change_key = Column(DateTime, nullable=False)

class FrozenAccounts(base):
    """
    user_id: int
    frozen_at: datetime
    delete_at: datetime
    """
    __tablename__ = 'frozenAccounts'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("userRegistered.id"), unique=True)
    frozen_at = Column(DateTime, nullable=False)
    delete_at = Column(DateTime, nullable=False)

    uid = relationship('UserRegistered')