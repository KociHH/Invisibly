from typing import Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

class UserFilter(BaseModel):
    param_name: str
    param_value: str | Any

class UserFullInfo(BaseModel):
    user_id: int | str | None = None
    w_pswd: bool = False 
    w_email_hash: bool = False

class UserUpdate(BaseModel):
    login: str | None = None
    name: str | None = None
    surname: str | None = None
    email: str | None = None
    bio: str | None = None

class GetOrCacheUserInfo(BaseModel):
    user_id: int | str
    handle: str
    return_items: list | None = None
    save_sql_redis: bool = True