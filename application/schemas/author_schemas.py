from pydantic import BaseModel


class CreateAuthorS(BaseModel):
    id: int
    first_name: str
    last_name: str


class ReturnAuthorS(BaseModel):
    first_name: str
    last_name: str

class UpdateAuthorS(BaseModel):
    first_name: str
    last_name: str


class UpdatePartiallyAuthorS(BaseModel):
    first_name: str | None
    last_name: str | None
