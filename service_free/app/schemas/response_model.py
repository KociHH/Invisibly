from pydantic import BaseModel

class AuthResponse(BaseModel):
    success: bool
    message: str
    access_token: str | None = None
    refresh_token: str | None = None
