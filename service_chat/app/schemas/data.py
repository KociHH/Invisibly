from pydantic import BaseModel

class AddChatsUser(BaseModel):
    user_id: int | str
    chat_ids: list[str | int]