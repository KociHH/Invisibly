from pydantic import BaseModel, EmailStr, ValidationError

class UserRegister(BaseModel):
    name: str
    login: str
    password: str
    email: EmailStr
    is_registered: bool

class UserLogin(BaseModel):
    login: str
    password: str
    email: EmailStr

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

class SettingsExit(BaseModel):
    user_id: str | int