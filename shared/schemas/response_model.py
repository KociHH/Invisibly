from pydantic import BaseModel

class SuccessAnswer(BaseModel):
    success: bool

class SuccessMessageAnswer(BaseModel):
    success: bool
    message: str
