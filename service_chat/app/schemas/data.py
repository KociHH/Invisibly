from pydantic import BaseModel

class CreatePrivateChat(BaseModel):
    user_id1: int | str
    user_id2: int | str
    
class DeleteChat(BaseModel):
    calling_user_id: str | int
    chat_ids: list[str | int]
    