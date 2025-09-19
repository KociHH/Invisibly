from pydantic import BaseModel


class SuccessAnswer(BaseModel):
    success: bool

class SuccessMessageAnswer(BaseModel):
    success: bool
    message: str

class EmailSendVerify(BaseModel):
    success: bool
    message: str
    send_for_verification: bool = False

class AuthResponse(BaseModel):
    success: bool
    message: str
    access_token: str | None = None
    refresh_token: str | None = None

class EventTokensResponse(BaseModel):
    access_token: str | None
    refresh_token: str | None
    token_type: str | None