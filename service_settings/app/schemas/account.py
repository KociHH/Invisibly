from pydantic import BaseModel

class SettingsExit(BaseModel):
    user_id: str | int

class DeleteAccount(BaseModel):
    user_id: int | str
    delete_confirmation: bool