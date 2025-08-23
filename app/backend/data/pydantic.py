from pydantic import BaseModel, EmailStr, ValidationError

# free points
class UserRegister(BaseModel):
    name: str
    login: str
    password: str
    email: EmailStr
    register: bool

class UserLogin(BaseModel):
    login: str
    password: str
    email: EmailStr

# token
class RefreshTokenRequest(BaseModel):
    refresh_token: str 

# user
class UserEditProfileNew(BaseModel):
    user_id: str | int
    name: str
    login: str
    email: EmailStr
    bio: str

class SettingsExit(BaseModel):
    user_id: str | int

# security
class NewEmail(BaseModel):
    user_id: int | str
    email: EmailStr
    confirm: bool = False

class NewPassword(BaseModel):
    user_id: int | str
    password: str
    confirm: bool = False

class ConfirmCode(BaseModel):
    confirm: bool = False

class DeleteAccount(BaseModel):
    user_id: int | str
    delete_confirmation: bool

# confirm_code
class ResendСode(BaseModel):
    resend: bool = False

class SendCode(BaseModel):
    code: str
    token: str


# confirm_password
class SendPassword(BaseModel):
    password: str
    token: str

# other
class SuccessAnswer(BaseModel):
    success: bool

class SuccessMessageAnswer(BaseModel):
    success: bool
    message: str

class WithoutExtraInfo(BaseModel):
    i: None = None

