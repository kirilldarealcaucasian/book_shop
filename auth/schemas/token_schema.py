from pydantic import BaseModel

class AccessToken(BaseModel):
    token: str
    type: str = "Bearer"


class TokenPayload(BaseModel):
    email: str
    is_admin: bool