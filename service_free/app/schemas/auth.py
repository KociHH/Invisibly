from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    login: str
    password: str
    email: EmailStr

class UserRegister(BaseModel):
    name: str
    surname: str | None = None
    login: str
    password: str
    email: EmailStr
    is_registered: bool