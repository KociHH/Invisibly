from pydantic import BaseModel

class EmailSendVerify(BaseModel):
    success: bool
    message: str
    send_for_verification: bool = False