from pydantic import EmailStr, BaseModel

class ChangeEmailForm(BaseModel):
    user_id: int | str
    email: EmailStr
    
class ChangeEmail(BaseModel):
    new_email: str

class ChangePassword(BaseModel):
    user_id: int | str
    password: str
    confirm: bool = False

class SendPassword(BaseModel):
    password: str
    token: str