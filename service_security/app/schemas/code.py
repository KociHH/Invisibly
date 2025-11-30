from pydantic import EmailStr, BaseModel

class ConfirmCode(BaseModel):
    confirm: bool = False
    
class SendCode(BaseModel):
    code: str
    token: str
    
class ConfirmPassword(BaseModel):
    password: str
    token: str