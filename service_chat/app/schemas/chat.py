from pydantic import BaseModel

class UserSendMessage(BaseModel):
    chat_id: str | int
    content: str
    