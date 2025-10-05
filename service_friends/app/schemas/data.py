from typing import Any
from pydantic import BaseModel

class FriendFilter(BaseModel):
    param_name: str
    param_value: str | Any

class FriendFullInfo(BaseModel):
    user_id: int | str | None = None
    friend_id: int | str

class FriendUpdate(BaseModel):
    user_id: str | int | None = None
    friend_id: str | int | None = None
    addition_number: str | int | None = None

class FriendsRequestsInfo(BaseModel):
    user_id: str | int
    get_fields: list[str] | None = None

class GetOrCacheFriends(BaseModel):
    user_id: str | int
    handle: str
    sort_reverse: bool