from pydantic import BaseModel

class CreateWodMessage(BaseModel):
    email: str
