from pydantic import EmailStr, BaseModel

class ChangeEmailForm(BaseModel):
    user_id: int | str
    email: EmailStr

class NewPassword(BaseModel):
    user_id: int | str
    password: str
    confirm: bool = False

class ChangeEmail(BaseModel):
    new_email: str

class DeleteAccount(BaseModel):
    user_id: int | str
    delete_confirmation: bool

class ConfirmCode(BaseModel):
    confirm: bool = False

class ResendCode(BaseModel):
    resend: bool = False

class SendCode(BaseModel):
    code: str
    token: str

# confirm_password
class SendPassword(BaseModel):
    password: str
    token: str