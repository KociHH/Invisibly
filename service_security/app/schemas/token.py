from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    refresh_token: str 

class DeleteTokenRedis(BaseModel):
    domain: str
    cache_call: bool = False