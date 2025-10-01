from pydantic import BaseModel

class SendEmail(BaseModel):
    success: bool
    code: int | str
    