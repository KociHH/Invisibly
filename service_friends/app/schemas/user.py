from pydantic import BaseModel

class FriendAdd(BaseModel):
    login: str

class FriendDelete(BaseModel):
    user_id: int | str