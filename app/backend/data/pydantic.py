from pydantic import BaseModel, EmailStr, ValidationError

# free points
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

# token
class RefreshTokenRequest(BaseModel):
    refresh_token: str 

# user
class UserEditProfileNew(BaseModel):
    user_id: str | int
    name: str
    surname: str
    login: str
    bio: str

class UserProfile(BaseModel):
    user_id: str | int

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

class AuthResponse(BaseModel):
    success: bool
    message: str
    access_token: str | None = None
    refresh_token: str | None = None

class EventTokensResponse(BaseModel):
    access_token: str | None
    refresh_token: str | None
    token_type: str | None

