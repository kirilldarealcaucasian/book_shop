from pydantic import BaseModel

class AccessToken(BaseModel):
    token: str
    type: str = "Bearer"


class TokenPayload(BaseModel):
    user_id: int
    email: str
    role: str