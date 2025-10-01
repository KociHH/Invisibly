from pydantic import BaseModel

class EventTokensResponse(BaseModel):
    access_token: str | None
    refresh_token: str | None
    token_type: str | None

class EmailSendVerify(BaseModel):
    success: bool
    message: str
    send_for_verification: bool = False