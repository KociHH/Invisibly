import datetime
from pydantic import BaseModel

class CreateUJWT(BaseModel):
    user_id: str | int
    jti: str | None
    token_type: str | None
    issued_at: int | datetime | None = None
    expires_at: int | datetime | None = None