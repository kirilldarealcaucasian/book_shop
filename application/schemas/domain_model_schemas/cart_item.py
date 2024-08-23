from pydantic import BaseModel, Field
from uuid import UUID


class CartItemS(BaseModel):
    session_id: UUID | None = None
    book_id: str | None = None
    quantity: int | None = Field(default=None, gt=0)