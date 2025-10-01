from pydantic import BaseModel

class UserEditProfileNew(BaseModel):
    user_id: str | int
    name: str
    surname: str
    login: str
    bio: str

class UserProfile(BaseModel):
    user_id: str | int
    full_name: str
    login: str
    bio: str