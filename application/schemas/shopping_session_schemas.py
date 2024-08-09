from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class CreateShoppingSessionS(BaseModel):
    user_id: int | None
    total: float


class ReturnShoppingSessionS(BaseModel):
    id: str
    user_id: int
    total: float
    expiration_time: datetime


class UpdatePartiallyShoppingSessionS(BaseModel):
    total: float = Field(ge=0)
    expiration_time: datetime | None


class ShoppingSessionIdS(BaseModel):
    id: uuid4