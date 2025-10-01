from pydantic import EmailStr, BaseModel

class ConfirmCode(BaseModel):
    confirm: bool = False

class ResendCode(BaseModel):
    resend: bool = False
    
class SendCode(BaseModel):
    code: str
    token: str